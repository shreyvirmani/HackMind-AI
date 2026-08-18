import json

import razorpay
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator

from database.models import PLAN_PRO, PLAN_MAX
from src.config.settings import settings
from src.payments.razorpay_client import client, is_configured
from src.auth.supabase_auth import get_current_user
from src.services.subscription_service import subscription_service
from src.utils.logger import logger

from database.connection import SessionLocal
from database.repository import payment_repository


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


# Server-side price list. The frontend only ever sends a plan
# identifier ("pro" / "max") -- it never sends an amount, and even if
# it did, the amount below (not anything from the request body) is
# what gets sent to Razorpay and stored on the Payment record.
PLAN_PRICES_INR = {
    PLAN_PRO: settings.PRO_PLAN_PRICE_INR,
    PLAN_MAX: settings.MAX_PLAN_PRICE_INR,
}


def _require_configured():
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail="Payments are not configured on this server yet.",
        )


class CreateOrderRequest(BaseModel):
    plan: str = PLAN_PRO
    months: int = 1

    @field_validator("plan")
    @classmethod
    def plan_must_be_purchasable(cls, value: str) -> str:
        if value not in PLAN_PRICES_INR:
            raise ValueError(
                f"plan must be one of {sorted(PLAN_PRICES_INR)}, got {value!r}"
            )
        return value


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
def create_order(
    request: CreateOrderRequest,
    current_user=Depends(get_current_user),
):
    """
    Step 1 of checkout: create a Razorpay order for the requested plan
    (Pro or Max) and return it to the frontend, which opens Razorpay
    Checkout with it. The amount is looked up server-side from
    PLAN_PRICES_INR -- the client only ever picks *which* plan, never
    the price.
    """

    _require_configured()

    months = max(1, request.months)
    amount_paise = PLAN_PRICES_INR[request.plan] * 100 * months

    try:
        order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1,
                "notes": {
                    "user_id": current_user["id"],
                    "plan": request.plan,
                    "months": str(months),
                },
            },
            # The Razorpay SDK has no default timeout -- without this,
            # a network/firewall issue reaching api.razorpay.com hangs
            # the request indefinitely instead of failing fast.
            timeout=10,
        )
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Could not reach Razorpay's API: {e}")
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not reach the payment gateway. This is usually "
                "a network/firewall issue on this server, not your "
                "payment details -- please try again in a moment."
            ),
        )
    except Exception as e:
        logger.error(f"Razorpay order creation failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="Could not create payment order. Please try again.",
        )

    db = SessionLocal()
    try:
        payment_repository.create_order_record(
            db=db,
            user_id=current_user["id"],
            razorpay_order_id=order["id"],
            amount=amount_paise,
            plan=request.plan,
            months=months,
            currency="INR",
        )
    except Exception as e:
        logger.error(f"Failed to persist payment order record: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not create payment order. Please try again.",
        )
    finally:
        db.close()

    return {
        "order_id": order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key": settings.RAZORPAY_KEY_ID,
        "plan": request.plan,
    }


@router.post("/verify")
def verify_payment(
    request: VerifyPaymentRequest,
    current_user=Depends(get_current_user),
):
    """
    Step 2 of checkout: the frontend calls this immediately after
    Razorpay Checkout succeeds, with the three values Razorpay's JS
    SDK returns. We verify the signature server-side before granting
    any access -- never trust a "success" callback from the client
    alone. Which plan gets granted is read back from the Payment row
    created in /create-order (itself set from a server-side price
    list), never from anything in this request. The webhook below is
    the authoritative backstop in case this call never arrives (tab
    closed, network drop, etc).
    """

    _require_configured()

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": request.razorpay_order_id,
                "razorpay_payment_id": request.razorpay_payment_id,
                "razorpay_signature": request.razorpay_signature,
            }
        )
    except razorpay.errors.SignatureVerificationError:
        db = SessionLocal()
        try:
            payment_repository.mark_failed(db, request.razorpay_order_id)
        finally:
            db.close()

        raise HTTPException(
            status_code=400,
            detail="Payment signature verification failed.",
        )

    db = SessionLocal()
    try:
        payment = payment_repository.get_by_order_id(
            db, request.razorpay_order_id
        )
        if not payment or payment.user_id != current_user["id"]:
            raise HTTPException(status_code=404, detail="Order not found.")

        plan = payment.plan
        months = payment.months

        payment_repository.mark_paid(
            db, request.razorpay_order_id, request.razorpay_payment_id
        )
    finally:
        db.close()

    subscription_service.upgrade_plan(current_user["id"], plan=plan, months=months)

    return {"status": "success", "plan": plan}


@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """
    Authoritative backstop for step 2: Razorpay calls this directly
    from its servers when a payment completes, independent of whether
    the user's browser tab is still open. Configure this URL in the
    Razorpay dashboard under Webhooks, subscribed to
    'payment.captured'. Like /verify, the plan and duration granted
    come from the Payment row (set server-side at order-creation
    time), never from the webhook payload itself.
    """

    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if not settings.RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Webhook secret not configured.",
        )

    try:
        client.utility.verify_webhook_signature(
            body.decode("utf-8"),
            signature,
            settings.RAZORPAY_WEBHOOK_SECRET,
        )
    except razorpay.errors.SignatureVerificationError:
        logger.warning("Razorpay webhook signature verification failed.")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    payload = json.loads(body)
    event = payload.get("event")

    if event == "payment.captured":
        payment_entity = payload["payload"]["payment"]["entity"]
        order_id = payment_entity["order_id"]
        payment_id = payment_entity["id"]

        db = SessionLocal()
        try:
            payment = payment_repository.get_by_order_id(db, order_id)

            if payment and payment.status != "paid":
                plan = payment.plan
                months = payment.months
                user_id = payment.user_id

                payment_repository.mark_paid(db, order_id, payment_id)
                subscription_service.upgrade_plan(user_id, plan=plan, months=months)
                logger.info(
                    f"Webhook upgraded user {user_id} to {plan} "
                    f"via order {order_id}."
                )
        except Exception as e:
            logger.error(f"Webhook processing failed for order {order_id}: {e}")
            raise HTTPException(status_code=500, detail="Webhook processing failed.")
        finally:
            db.close()

    return {"status": "ok"}

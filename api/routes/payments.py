import json

import razorpay
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

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


def _require_configured():
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail="Payments are not configured on this server yet.",
        )


class CreateOrderRequest(BaseModel):
    months: int = 1


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
    Step 1 of checkout: create a Razorpay order for the Pro plan and
    return it to the frontend, which opens Razorpay Checkout with it.
    """

    _require_configured()

    months = max(1, request.months)
    amount_paise = settings.PRO_PLAN_PRICE_INR * 100 * months

    try:
        order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1,
                "notes": {
                    "user_id": current_user["id"],
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
            currency="INR",
        )
    finally:
        db.close()

    return {
        "order_id": order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key": settings.RAZORPAY_KEY_ID,
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
    Pro access -- never trust a "success" callback from the client
    alone. The webhook below is the authoritative backstop in case
    this call never arrives (tab closed, network drop, etc).
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

        payment_repository.mark_paid(
            db, request.razorpay_order_id, request.razorpay_payment_id
        )
    finally:
        db.close()

    subscription_service.upgrade_to_pro(current_user["id"], months=1)

    return {"status": "success", "plan": "pro"}


@router.post("/webhook")
async def razorpay_webhook(request: Request):
    """
    Authoritative backstop for step 2: Razorpay calls this directly
    from its servers when a payment completes, independent of whether
    the user's browser tab is still open. Configure this URL in the
    Razorpay dashboard under Webhooks, subscribed to
    'payment.captured'.
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
                payment_repository.mark_paid(db, order_id, payment_id)
                subscription_service.upgrade_to_pro(payment.user_id, months=1)
                logger.info(
                    f"Webhook upgraded user {payment.user_id} to Pro "
                    f"via order {order_id}."
                )
        finally:
            db.close()

    return {"status": "ok"}
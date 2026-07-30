import razorpay

from src.config.settings import settings


# A single shared Razorpay client, built once at import time -- same
# pattern used everywhere else you talk to an external API in this
# codebase. Constructing the client never fails even if the keys are
# blank (Razorpay doesn't validate credentials until you actually
# call the API), so this is safe to import even before you've set
# RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET in your .env -- the routes in
# api/routes/payments.py check `is_configured` first and return a
# clean 503 instead of a confusing auth error deep in the SDK.
client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET,
    )
)


def is_configured() -> bool:
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
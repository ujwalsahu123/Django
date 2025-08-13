import razorpay
from django.conf import settings

def get_razorpay_client():
    """
    Returns an initialized Razorpay client instance
    """
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    return client

def create_razorpay_order(amount, currency=settings.RAZORPAY_CURRENCY):
    """
    Creates a Razorpay order
    :param amount: Amount in smallest currency unit (paise for INR)
    :param currency: Currency code (default: INR)
    :return: Razorpay order object
    """
    client = get_razorpay_client()
    
    data = {
        "amount": amount,
        "currency": currency,
        "receipt": f"order_rcptid_{settings.RAZORPAY_TEST_MODE}",
        "notes": {
            "mode": "test" if settings.RAZORPAY_TEST_MODE else "live"
        },
        "payment_capture": 1
    }
    
    order = client.order.create(data=data)
    return order

def verify_payment_signature(payment_id, order_id, signature):
    """
    Verifies the payment signature
    """
    client = get_razorpay_client()
    
    try:
        return client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
    except Exception as e:
        return False

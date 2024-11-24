from celery import shared_task
from .models import Payment  # ensure this is imported properly

@shared_task
def fail_payment_if_unpaid(payment_id):
    print(f"Received payment_id: {payment_id}")
    try:
        payment = Payment.objects.get(pk=payment_id)
        payment.status = "failed"
        payment.save()
        print(f"Payment {payment_id} status set to failed.")
        return True
    except Payment.DoesNotExist:
        print(f"Payment {payment_id} does not exist.")
        return False
@shared_task
def simple_task(payment_id):
    print(f"Simple task running with payment_id: {payment_id}")
    return True

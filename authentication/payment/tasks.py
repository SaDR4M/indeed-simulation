from celery import shared_task
from .models import Payment  # ensure this is imported properly

@shared_task
def fail_payment_if_unpaid(payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
        if payment.status != "completed" :
            payment.status = "failed"
            payment.save()
            return True
        return False
    except Payment.DoesNotExist:
        return False


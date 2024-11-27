from celery import shared_task
from . import utils
from django.db import transaction
# local imports 
from account.models import Message
from account.tasks import send_order_email , send_order_sms
from employer.models import EmployerOrder
from .models import Payment  # ensure this is imported properly

@shared_task(bind=True, default_retry_count=15, max_retries=20)
def fail_payment_if_unpaid(self, payment_id, retry_count=0):
    try:
        # Use the passed payment_id
        payment = Payment.objects.get(pk=payment_id)
        order = payment.order
    except Payment.DoesNotExist:
        return "Payment doesn't exist"
    except EmployerOrder.DoesNotExist:
        return "Order doesn't exist"

    payment_status = utils.verify_payment(payment.authority, payment.amount)
    if payment_status:
        with transaction.atomic():
            payment.status = "completed"
            order.status = 'completed'  
            order.save()
            payment.save()
            user = payment.employer.user
            order_id = order.order_id
            if user.phone :
                # send sms for the order
                message = Message.objects.create(phone=user.phone ,type="order" , kind="sms")
                send_order_sms.apply_async(args=[user.phone , order_id , message.pk])
            if user.email : 
                # send email for the order 
                message = Message.objects.create(email=user.email ,type="order" , kind="email")
                send_order_email.apply_async(args=[user.email , order_id , message.pk])
        return "completed"

    # Handle retries
    if retry_count < self.max_retries :
        self.retry(args=[payment.pk, retry_count + 1], countdown=30)
    else:
        with transaction.atomic():
            payment.status = "failed"
            order.status = "failed"
            payment.save()
            order.save()
        return "payment failed"
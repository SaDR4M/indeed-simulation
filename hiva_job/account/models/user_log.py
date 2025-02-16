# django & rest imports
from django.db import models
from django.core.validators import RegexValidator


class UserLog(models.Model):

    user = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    ip_address = models.CharField(
        max_length=100,
    )

    browser = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    os = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    device = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    for_admin = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    log_kind_choices = (
        (0, "ورود کاربر"),
        (1, "رمز اشتباه"),
        (2, "خروج کاربر"),
        (3, "توکن اشتباه"),
        (4, "در خواست فراموشی رمز عبور با پیامک"),
        (5, "تغییر رمز عبور پس از فراموشی رمز عبور با پیامک"),

    )
    log_kind = models.SmallIntegerField(default=0,
                                        choices=log_kind_choices,
                                        help_text="نوع لاگ",)

    def __str__(self) -> str:
        return self.for_admin

class Message(models.Model) :
     
    phone_validator = RegexValidator(
        regex=r'^\d{11}$',
        message="Phone number must be entered in the format: '09121314156'"
    )
    
    class MessageKind(models.TextChoices) :
        EMAIL = "email" , "Email"
        SMS = "sms" , "Sms"
    
    class MessageType(models.TextChoices) :
        OTP = "otp" , "Otp"
        LOGIN = "login" , "Loign"
        ORDER = "order" , "Order"
        RESUME = "resume" , "Resume"
        EXPIRE = "expire" , "Expire"
        
    class MessageStatus(models.TextChoices) :
        PENDING = "pending" , "Pending"
        SENT = "sent" , "Sent"
        DELIVERED = "delivered" , "Delivered"
        UNDELIVERED = "undelivered" , "Undelivered"
        FAILED = "failed" , "Failed"
        
        
    phone = models.CharField(max_length=15, null=True , blank=True , validators=[phone_validator])
    email = models.CharField(max_length=255 ,null=True , blank=True)
    send_at = models.DateTimeField(auto_now_add=True)
    kind = models.CharField(choices=MessageKind)
    type = models.CharField(choices=MessageType)
    status = models.CharField(choices=MessageStatus , default=MessageStatus.PENDING)
    content = models.TextField(null=True , blank=True)
    message_id = models.CharField(null=True , blank=True)
    
    class Meta :
        db_table = "message"
    
    


from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager
from pkg_resources import require


# Create your models here.

class UserManager(BaseUserManager) :

    def create_user(self , phone=None , email=None , password=None):

        if not phone and not email:
            raise ValueError("email/phone number must be provided")
        if phone :
            user = self.model(phone=phone)
        if email : 
            user = self.model(email=email)
        if password :
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self , phone , password=None):

        if not phone :
            raise ValueError("phone number must be provided")
        if not password :
            raise ValueError("password must be provided")


        user = self.create_user(phone=phone , password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractUser) :

    phone_validator = RegexValidator(
        regex=r'^\d{11}$',
        message="Phone number must be entered in the format: '09121314156'"
    )

    username = None

    phone = models.CharField(max_length=15, unique=True, blank=True, null=False , validators=[phone_validator])
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    USERNAME_FIELD = 'phone'
    # password for admins
    REQUIRED_FIELDS = ['password']


    objects = UserManager()

    def __str__(self):
        return f'{self.phone} - {self.email}'


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
    
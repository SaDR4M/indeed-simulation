
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager
# third party imports
from guardian.shortcuts import assign_perm
# local imports

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
        # TODO add other model permission needed for admin 
        assign_perm("job_seeker.view_test" , user)
        assign_perm("job_seeker.view_questionandanswers" , user)
        user.save(using=self._db)
        return user

class User(AbstractUser) :

    phone_validator = RegexValidator(
        regex=r'^\d{11}$',
        message="Phone number must be entered in the format: '09121314156'"
    )

    username = None

    phone = models.CharField(max_length=15, unique=True, blank=True, null=True , validators=[phone_validator])
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)

    USERNAME_FIELD = 'phone'
    # password for admins
    REQUIRED_FIELDS = ['password']


    objects = UserManager()

    def __str__(self):
        return f'{self.phone} - {self.email}'
    
    class Meta :
        models.Index(fields=['phone' , 'email'])


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
    
    
# test

class Countries(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    iso3 = models.CharField(max_length=3, blank=True, null=True)
    numeric_code = models.CharField(max_length=3, blank=True, null=True)
    iso2 = models.CharField(max_length=2, blank=True, null=True)
    phonecode = models.CharField(max_length=255, blank=True, null=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=255, blank=True, null=True)
    currency_name = models.CharField(max_length=255, blank=True, null=True)
    currency_symbol = models.CharField(max_length=255, blank=True, null=True)
    tld = models.CharField(max_length=255, blank=True, null=True)
    native = models.CharField(max_length=255, blank=True, null=True)
    # region = models.CharField(max_length=255, blank=True, null=True)
    # region_0 = models.ForeignKey('Regions', models.DO_NOTHING, db_column='region_id', blank=True, null=True)  # Field renamed because of name conflict.
    #subregion = models.CharField(max_length=255, blank=True, null=True)
    #subregion_0 = models.ForeignKey('Subregions', models.DO_NOTHING, db_column='subregion_id', blank=True, null=True)  # Field renamed because of name conflict.
    nationality = models.CharField(max_length=255, blank=True, null=True)
    timezones = models.TextField(blank=True, null=True)
    translations = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    emoji = models.CharField(max_length=191, blank=True, null=True)
    emojiu = models.CharField(db_column='emojiU', max_length=191, blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField()
    flag = models.SmallIntegerField()
    wikidataid = models.CharField(db_column='wikiDataId', max_length=255, blank=True, null=True, db_comment='Rapid API GeoDB Cities')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'countries'
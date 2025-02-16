# django imports
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
# local imports
from account.models.manager import UserManager





# Create your models here.
class User(AbstractBaseUser):
    '''
    Base User Class Model
    '''
    username = models.CharField(
        max_length=20,
        blank=False,
        null = True,
        unique=True,
    )
    mobile = models.TextField(_('mobile number') ,  max_length=11 , unique=True)

    mobile_code = models.CharField(
        max_length=6,
        default='+98',
        blank=False,
        help_text='کد موبایل کاربر - DialCode',
    )
    role_choices = (
        (0, "buyer"),
        (2, "operator"),
        (10, "admin"),
    )
    role = models.SmallIntegerField(
        default=0,
        choices=role_choices,
        help_text='handling the user role'
    ) 
    """NOTE for future plans"""
    # plan_choices = (
    #     (0, "Have not active plan"),
    #     (1, "Have a active Plan"),
    #     (2, "Plan Expired"),
    # )
    # plan_status = models.SmallIntegerField(
    #     default=0,
    #     choices=plan_choices,
    #     help_text='handling the user plan status'
    # )    

    # last_plan = models.ForeignKey(
    #     'Membership',
    #     on_delete=models.CASCADE,
    #     blank=True,
    #     null=True,
    #     related_name='user_active_plan', 
    #     help_text='last plan (active or expired)'
    # ) 

    # plans = models.ManyToManyField(
    #     PricingPlan,
    #     through='Membership',
    #     blank=True,
    #     help_text="All of my plans",
    #     related_name="plans_set",
    #     related_query_name="plans",
    # )
    email = models.EmailField(blank = True, null = True,)
    name = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        default = '-',
        help_text='اسم کوچک ',
    )
    family_name = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        default = '-',
        help_text='نام خانوادگی ',
    )
    personal_national_id = models.CharField(
        blank=True,
        null=True,
        max_length=30,
        help_text='شناسه ملی (حقیقی)',
    )

    phone = models.CharField(
        blank=True,
        null=True,
        max_length=30,
        help_text='شماره تلفن ثابت',
    ) 
    
    birthday = models.DateTimeField(
        blank=True,
        null=True,
        help_text='تاریخ تولد (حقیقی)',
    )

    banned = models.BooleanField(
        default=False,
        help_text='یوزر از سایت بن شده'
    )
    need_complete = models.BooleanField(
        default=True,
        help_text='جهت تشخیص نیاز به تکمیل پروفایل کاربری'
    )
    ban_cause = models.TextField(
        blank=True,
        null=True,
        help_text='علت بن شدن یوزر از سایت'
    )
    banned_by = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='user_banned_by',
        help_text='یوزر توسط چه کسی بن شده'
    )
    is_real = models.BooleanField(
        default=True,
        help_text='یوزر حقیقی‌ است یا حقوقی'
    )
    gender = models.BooleanField(
        blank=True, null=True, help_text="male = True, female = False")

    created = models.DateTimeField(auto_now_add=True)

    modified = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(
        default=False
    )
    created_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE) 

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        # empty string to prevent empty values
        mobile = str(self.mobile) if self.mobile is not None else ''
        name = str(self.name) if self.name is not None else ''
        family_name = str(self.family_name) if self.family_name is not None else ''
        return mobile +' - '+ name +' '+ family_name
    
        
    def save(self, *args, **kwargs):
        self.username = str(self.mobile)+'-'+str(self.role)
        super().save(*args, **kwargs)
        
        

    
    


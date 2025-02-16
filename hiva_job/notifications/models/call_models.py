
# django & rest imports
from django.db import models
# local imports
from core.models import TimeStampedModel
# Create your models here.


class CallCategory(TimeStampedModel):
    """ Category of different type of sms in system
    code must be unique ans we use them to find the related category type and send sms to users.
    """
    
    code = models.IntegerField(
        blank=False,
        help_text="کد دسته بندی تماس",
        null=False,
    )
    title = models.CharField(
        max_length=128,
        blank=False,
        null=False,
        help_text="عنوان دسته بندی تماس",
    )
    description = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        help_text="توضیحات دسته بندی تماس",
    )
    callText = models.TextField(
        blank=True,
        null=True,
        help_text="متن تماس",
    )
    KIND_CHOICES = ((1, "واردات"),
                    (2, "صادرات"),
                    (3, "داخلی"),
                    (4, "اپراتور"),
                    (5, "ادمین"),
                    (6, "بازاریابی"),
                    (7, "متفرقه"))
    kind = models.SmallIntegerField(
        choices=KIND_CHOICES, blank=True, null=True,)

    isActive = models.BooleanField(
        blank=False,
        default=True,
        help_text="آیا دسته بندی تماس فعال است؟",
    )
    activeBy = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    number_choices = (
        (1, "9124462808"),
    )
    sendByNumber = models.SmallIntegerField(
        default=1,
        blank=False,
        null=False,
        choices=number_choices,
        help_text="شماره خط جهت تماس",
    )

    delay_time = models.IntegerField(default = 0, blank=True, null = False, help_text='if want the sms have some delay, must be set with minutes')
    
    
    def __str__(self):
        return f"{self.code} : {self.title}"


class CallLog(models.Model):

    params_receptor = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="",
    )

    params_message = models.TextField(
        blank=True,
        null=True,
    )

    params_sender = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="",
    )

    params_template = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="",
    )

    params_token = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="",
    )

    params_type = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="",
    )

    validation = models.BooleanField(
        blank=True,
        null=True,
        help_text="",
    )

    status_choices = (
        (1, "مخاطب در تماس دیگری است"),
        (2, "اپلیکیشن توکن ارسال شده نامعتبر می باشد."),
        (4, "شناسه اپلیکیشن معتبر نمی باشد "),
        (5, "شناسه تماس معتبر نیست "),
        (
            6,
            "خطای نامشخص (Failed)",
        ),
        (10, "مقدار پلتفرم کاربر نامعتبر می باشد. مقادیر معتبر : 'ios' یا 'android'"),
        (
            11,
            "شناسه وارد شده تکراری می باشد (endpoint)",
        ),
        (
            13,
            " نوع پارامترها همخانی ندارد",
        ),
        (
            14,
            "دسترسی مجاز نیست",
        ),
        (
            100,
            "شناسه اپلیکیشن معتبر نمی باشد",
        ),
    )

    status = models.SmallIntegerField(
        null=True,
        choices=status_choices,
        help_text="",
    )

    messageid = models.BigIntegerField(
        null=True,
        help_text="",
    )

    message = models.TextField(
        blank=True,
        null=True,
    )

    sender = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="",
    )

    receptor = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="",
    )
    callCat = models.ForeignKey(
        CallCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="دسته بندی تماس",
        related_name="call_callCategory",
    )
    send_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    date = models.DateTimeField(
        blank=True,
        null=True,
    )

    cost = models.IntegerField(
        blank=True,
        null=True,
        help_text="",
    )

    created_date = models.DateTimeField(auto_now_add=True)

    is_sending = models.BooleanField(default=True)  # send or recieved types
    
    maxDuration =  models.IntegerField(
        blank=True,
        null=True,
        help_text="",
    )

    def __str__(self):
        return f"{self.params_receptor} - {self.params_sender} -  {self.smsCat}"



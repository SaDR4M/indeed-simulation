from django.db import models
# local import
from account.models import User
from employer.models import Employer
from requests.utils import default_user_agent


# Create your models here.
class Payment(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    checkout_at = models.DateTimeField()




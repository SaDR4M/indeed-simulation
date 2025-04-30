from django.db import models

# Create your models here.
class TechnologyCategory(models.Model) :
    name = models.CharField(
        max_length=250 , 
        unique=True,
        db_index=True
    )
    description = models.TextField(
        blank=True , null=True
    )
    created_by = models.ForeignKey(
        "account.User" , 
        on_delete=models.CASCADE, 
        related_name="categories_added"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

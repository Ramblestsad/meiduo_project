from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """description: custom user model class"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name='cellphone number')

    class meta:

        db_table = 'tb_users'  # custom table name
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

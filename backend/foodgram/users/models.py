from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    alphanumeric = RegexValidator(
        r'^[0-9a-zA-Z_]*$',
        'Разрешены символы алфавита, цифры и нижние подчеркивания.'
    )
    alphabetic = RegexValidator(
        r'^[a-zA-Zа-яА-Я]*$',
        'Разрешены символы русского и ангийского алфавитов.'
    )

    email      = models.EmailField(verbose_name="email", max_length=254, unique=True)
    username   = models.CharField(max_length=150,
                                  unique=True,    validators=[alphanumeric])
    first_name = models.CharField(max_length=150, validators=[alphabetic])
    last_name  = models.CharField(max_length=150, validators=[alphabetic])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def __str(self):
        return f'{self.user} подписан на {self.author}'

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """
    Модель организации с балансом.

    Attributes:
        inn (str): ИНН организации (10 или 12 цифр), уникальный
        balance (Decimal): Текущий баланс организации (не может быть отрицательным)
    """

    inn = models.CharField(
        max_length=12,
        unique=True,
        verbose_name=_('ИНН организации'),
        help_text=_('ИНН организации (10 или 12 цифр)'),
        db_index=True
    )

    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Баланс'),
        help_text=_('Текущий баланс организации в рублях')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания'),
        db_index=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        verbose_name = _('Организация')
        verbose_name_plural = _('Организации')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inn']),
            models.Index(fields=['balance']),
        ]

    def __str__(self):
        return _('Организация %(inn)s (баланс: %(balance)s)') % {
            'inn': self.inn,
            'balance': self.balance
        }

    def clean(self):
        """Дополнительная валидация модели."""
        super().clean()
        if not self.inn.isdigit():
            raise models.ValidationError(
                _('ИНН должен содержать только цифры')
            )


class Payment(models.Model):
    """
    Модель платежа от банка.

    Attributes:
        operation_id (UUID): Уникальный идентификатор операции
        amount (Decimal): Сумма платежа (не может быть отрицательной)
        payer_inn (str): ИНН плательщика
        document_number (str): Номер платежного документа
        document_date (datetime): Дата документа
    """

    operation_id = models.UUIDField(
        unique=True,
        verbose_name=_('ID операции'),
        help_text=_('Уникальный идентификатор операции'),
        db_index=True
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Сумма платежа'),
        help_text=_('Сумма в рублях')
    )

    payer_inn = models.CharField(
        max_length=12,
        verbose_name=_('ИНН плательщика'),
        help_text=_('ИНН организации-плательщика'),
        db_index=True
    )

    document_number = models.CharField(
        max_length=100,
        verbose_name=_('Номер документа'),
        help_text=_('Номер платежного документа'),
        db_index=True
    )

    document_date = models.DateTimeField(
        verbose_name=_('Дата документа'),
        help_text=_('Дата создания документа')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания записи'),
        db_index=True
    )

    class Meta:
        verbose_name = _('Платеж')
        verbose_name_plural = _('Платежи')
        ordering = ['-document_date', '-created_at']
        indexes = [
            models.Index(fields=['operation_id']),
            models.Index(fields=['payer_inn']),
            models.Index(fields=['document_number']),
            models.Index(fields=['document_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='payment_amount_non_negative'
            ),
        ]

    def __str__(self):
        return _('Платеж №%(doc_num)s на %(amount)s руб. от %(inn)s') % {
            'doc_num': self.document_number,
            'amount': self.amount,
            'inn': self.payer_inn
        }

    def clean(self):
        """Дополнительная валидация модели."""
        super().clean()
        if not self.payer_inn.isdigit():
            raise models.ValidationError(
                _('ИНН плательщика должен содержать только цифры')
            )

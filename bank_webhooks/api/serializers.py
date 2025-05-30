from rest_framework import serializers
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from .models import Organization


class WebhookSerializer(serializers.Serializer):
    """
    Сериализатор для валидации входящих webhook-ов от банка.

    Валидирует:
    - operation_id: уникальный идентификатор операции (UUID)
    - amount: сумма платежа (положительное число)
    - payer_inn: ИНН плательщика (12 цифр)
    - document_number: номер платежного документа
    - document_date: дата и время документа
    """

    operation_id = serializers.UUIDField(
        required=True,
        label=_('ID операции'),
        help_text=_('Уникальный идентификатор операции в формате UUID')
    )

    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        required=True,
        label=_('Сумма платежа'),
        help_text=_('Положительная сумма платежа в рублях')
    )

    payer_inn = serializers.CharField(
        max_length=12,
        min_length=10,
        required=True,
        label=_('ИНН плательщика'),
        help_text=_('ИНН организации (10 или 12 цифр)'),
        validators=[MinLengthValidator(10)]
    )

    document_number = serializers.CharField(
        max_length=100,
        required=True,
        label=_('Номер документа'),
        help_text=_('Номер платежного документа')
    )

    document_date = serializers.DateTimeField(
        required=True,
        label=_('Дата документа'),
        help_text=_('Дата и время создания документа')
    )

    def validate_payer_inn(self, value):
        """Дополнительная валидация ИНН."""
        if not value.isdigit():
            raise serializers.ValidationError(
                _('ИНН должен содержать только цифры')
            )
        return value


class OrganizationBalanceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения баланса организации.

    Поля:
    - inn: ИНН организации
    - balance: текущий баланс в рублях
    """

    class Meta:
        model = Organization
        fields = ['inn', 'balance']
        read_only_fields = ['inn', 'balance']
        extra_kwargs = {
            'inn': {
                'label': _('ИНН организации'),
                'help_text': _('Идентификационный номер налогоплательщика')
            },
            'balance': {
                'label': _('Баланс'),
                'help_text': _('Текущий баланс организации в рублях')
            }
        }

    def to_representation(self, instance):
        """Форматирование вывода данных."""
        ret = super().to_representation(instance)
        ret['balance'] = float(ret['balance'])
        return ret

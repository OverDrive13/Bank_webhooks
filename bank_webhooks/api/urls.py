from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import BankWebhookView, OrganizationBalanceView

app_name = 'bank_api'

urlpatterns = [
    path(
        'webhook/bank/',
        BankWebhookView.as_view(),
        name='bank-webhook',
        kwargs={
            'description': _('Эндпоинт для обработки входящих webhook-ов от банка'),
            'help_text': _('Принимает платежные уведомления и обновляет балансы организаций')
        }
    ),
    path(
        'organizations/<str:inn>/balance/',
        OrganizationBalanceView.as_view(),
        name='organization-balance',
        kwargs={
            'description': _('Получение текущего баланса организации'),
            'help_text': _('Возвращает баланс организации по указанному ИНН'),
            'examples': {
                'inn': ['1234567890', '0987654321']
            }
        }
    ),
]

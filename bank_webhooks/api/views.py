import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .models import Organization, Payment
from .serializers import WebhookSerializer, OrganizationBalanceSerializer

logger = logging.getLogger(__name__)


class BankWebhookView(APIView):
    """Обработчик входящих webhook-ов от банка."""

    @transaction.atomic
    def post(self, request):
        """
        Обрабатывает входящий платеж:
        - Валидирует данные
        - Проверяет на дубликаты
        - Создает платеж
        - Обновляет баланс организации
        """
        try:
            serializer = WebhookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            return self._process_payment(data)

        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}", exc_info=True)
            raise ValidationError({"detail": "Payment processing failed"})

    def _process_payment(self, payment_data):
        """Основная логика обработки платежа."""
        operation_id = payment_data['operation_id']

        if Payment.objects.filter(operation_id=operation_id).exists():
            logger.info(
                f'Duplicate payment operation: {operation_id}. Skipping.'
            )
            return Response(
                {'status': 'duplicate', 'operation_id': str(operation_id)},
                status=status.HTTP_200_OK
            )

        organization = self._get_or_create_organization(
            payment_data['payer_inn'])
        payment = self._create_payment(payment_data)
        self._update_organization_balance(organization, payment_data['amount'])

        logger.info(
            f'Payment processed. Organization: {organization.inn}, '
            f'Amount: {payment_data["amount"]}, '
            f'New balance: {organization.balance}, '
            f'Payment ID: {payment.id}'
        )

        return Response(
            {
                'status': 'success',
                'payment_id': payment.id,
                'organization_inn': organization.inn,
                'new_balance': float(organization.balance)
            },
            status=status.HTTP_201_CREATED
        )

    def _get_or_create_organization(self, inn):
        """Получает или создает организацию."""
        organization, created = Organization.objects.get_or_create(
            inn=inn,
            defaults={'balance': 0}
        )
        if created:
            logger.debug(f'Created new organization with INN: {inn}')
        return organization

    def _create_payment(self, payment_data):
        """Создает запись о платеже."""
        return Payment.objects.create(
            operation_id=payment_data['operation_id'],
            amount=payment_data['amount'],
            payer_inn=payment_data['payer_inn'],
            document_number=payment_data['document_number'],
            document_date=payment_data['document_date']
        )

    def _update_organization_balance(self, organization, amount):
        """Обновляет баланс организации."""
        organization.balance += amount
        organization.save()


class OrganizationBalanceView(APIView):
    """API для получения баланса организации."""

    def get(self, request, inn):
        """
        Возвращает текущий баланс организации по ИНН.

        Args:
            inn: ИНН организации (строка, 10 или 12 цифр)

        Returns:
            404 если организация не найдена
            200 с данными баланса при успехе
        """
        try:
            organization = get_object_or_404(Organization, inn=inn)
            serializer = OrganizationBalanceSerializer(organization)
            return Response(serializer.data)

        except Exception as e:
            logger.error(
                f"Error fetching balance for organization {inn}: {str(e)}",
                exc_info=True
            )
            raise

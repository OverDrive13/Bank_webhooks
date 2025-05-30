from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path(
        'admin/',
        admin.site.urls,
        name='admin',
        kwargs={
            'description': _('Административный интерфейс Django'),
            'help_text': _('Панель управления для администраторов системы')
        }
    ),
    path(
        'api/',
        include(('api.urls', 'api'), namespace='api'),
        name='api-root',
        kwargs={
            'description': _('Базовый URL для API системы'),
            'help_text': _('Содержит все API endpoints системы')
        }
    ),
]

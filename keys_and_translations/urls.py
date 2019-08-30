from django.urls import path

from . import views

urlpatterns = [
    path('', views.keys, name='keys'),
    path('<int:keyId>/', views.key_update, name='key_update'),
    path('<int:keyId>/translations/', views.translations, name='translations'),
    path('<int:keyId>/translations/<str:locale>/', views.translations_in_locale, name='translations_in_locale'),
]
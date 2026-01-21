from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nova/', views.nova_transacao, name='nova_transacao'),
    path('nova/load-subcategorias/', views.load_subcategorias, name='load_subcategorias'),
    path('planejamento/', views.planejamento, name='planejamento'),
]
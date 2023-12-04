from django.urls import path
from .views import onOffPivo, getAllFazendas, createFazenda, loginFazenda, getFazendaById, getAllPivos, createPivo, deletePivo, deleteEvento, getIrrigacaoEvento, createEvento, updateEventoIrrigacao

urlpatterns = [
    path('createFazenda', createFazenda, name=''),
    path('loginFazenda', loginFazenda, name=''),
    path('getAllFazendas', getAllFazendas, name='getFazenda'),
    path('getFazendaById/<str:fazenda_id>/', getFazendaById, name='getFazendaById'),
    path('getAllPivos', getAllPivos, name=''),
    path('createEvento', createEvento, name=''),
    path('deleteEvento/<str:evento_id>/', deleteEvento, name=''),
    path('updateEventoIrrigacao/<int:id>', updateEventoIrrigacao, name=''),
    path('createPivo', createPivo, name=''),
    path('deletePivo/<str:pivo_id>/', deletePivo, name=''),
    path('updateEventoIrrigacao', updateEventoIrrigacao, name=''),
    path('getIrrigacaoEvento', getIrrigacaoEvento, name=''),
    path('onOffPivo/<str:pivo_key>/', onOffPivo, name='')
]


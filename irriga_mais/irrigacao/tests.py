from django.test import TestCase
import json
from datetime import datetime, timedelta
from django.test import TestCase, RequestFactory
from django.contrib.auth.hashers import make_password
from .models import Fazenda, PivoIrrigacao, EventoIrrigacao, TokenAuth
from .views import onOffPivo, getAllFazendas, getFazendaById, createFazenda, loginFazenda, createPivo, deletePivo, getAllPivos, createEvento, deleteEvento, updateEventoIrrigacao, getIrrigacaoEvento

class ViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.fazenda = Fazenda.objects.create(nome='Teste', email='teste@teste.com', senha=make_password('senha123'), localizacao_latitude='1.0', localizacao_longitude='2.0')
        self.pivo = PivoIrrigacao.objects.create(nome='Pivo Teste', descricao='Descrição do Pivo', token='token123', fazenda=self.fazenda, tipo='Tipo Teste')
        self.evento = EventoIrrigacao.objects.create(pivo=self.pivo, duracao=timedelta(minutes=30), data_hora_inicio=datetime.now())

    def test_onOffPivo(self):
        request = self.factory.get('/onOffPivo/')
        onOffPivo(request, self.pivo.token, self.evento.id)

    def test_getAllFazendas(self):
        request = self.factory.get('/getAllFazendas/')
        response = getAllFazendas(request)
        self.assertEqual(response.status_code, 200)

    def test_getFazendaById(self):
        request = self.factory.get(f'/getFazendaById/{self.fazenda.id}/')
        response = getFazendaById(request, self.fazenda.id)
        self.assertEqual(response.status_code, 200)

    def test_getIrrigacaoEvento(self):
        request = self.factory.get('/getIrrigacaoEvento/')
        response = getIrrigacaoEvento(request)
        self.assertEqual(response.status_code, 200)

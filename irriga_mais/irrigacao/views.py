from .models import Fazenda, PivoIrrigacao, EventoIrrigacao, TokenAuth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
import secrets
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404


def onOffPivo(request, pivo_key, evento_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'pivo_{pivo_key}',
        {
            'type': 'receive',
            'pivo_key': pivo_key,
            'evento_id': evento_id
        }
    )


def getAllFazendas(request):
    queryset = Fazenda.objects.all()
    fazendas = list(queryset.values())
    return JsonResponse({'fazendas': fazendas}, status=200)


def getFazendaById(request, fazenda_id):
    queryset = Fazenda.objects.filter(pk=fazenda_id).all()
    fazenda = list(queryset.values())
    return JsonResponse({'response': fazenda}, status=200)


def createFazenda(request):
    data = request.GET
    fazenda = Fazenda.objects.create(nome=data['nome'], 
                                     email=data['email'],
                                     senha=make_password(data['senha']),
                                     localizacao_latitude=data['latitude'],
                                     localizacao_longitude=data['longitude'])
    return JsonResponse({'id': fazenda.id}, status=201)


def loginFazenda(request):
    data = request.GET
    queryset = Fazenda.objects.filter(email=data['email']).all()

    if queryset.exists():
        fazenda = list(queryset.values())
        if (check_password(data['senha'], fazenda[0]['senha'])):
            token = secrets.token_hex(100 // 2)
            TokenAuth.objects.create(token=token, data_expiracao=timezone.now() + timezone.timedelta(days=1))
            return JsonResponse({'message': 'Autorizado!', 'token': token, 'id': fazenda[0]['id']}, status=201)
        else:
            return JsonResponse({'message': 'Senha incorreta!'}, status=401)
    else:
        return JsonResponse({'message': 'Não autorizado!'}, status=401)


def createPivo(request):
    data = request.GET
    token = secrets.token_hex(20 // 2)
    pivo = PivoIrrigacao.objects.create(nome=data['nome'], 
                                        descricao=data['descricao'],
                                        token=token,
                                        fazenda=Fazenda.objects.get(pk=data['fazenda_id']),
                                        tipo=data['tipo'])
    return JsonResponse({'id': pivo.id}, status=201)


def deletePivo(request, pivo_id):
    pivo = PivoIrrigacao.objects.get(pk=pivo_id)
    pivo.delete()
    return JsonResponse({}, status=204)


def getAllPivos(request):
    fazenda_id = request.headers.get('fazendaId')
    fazenda = get_object_or_404(Fazenda, id=fazenda_id)

    queryset = PivoIrrigacao.objects.all().filter(fazenda=fazenda)
    pivos = list(queryset.values())
    return JsonResponse({'response': pivos}, status=200)


def createEvento(request):
    data = request.GET
    duracao_em_minutos = int(data['duracao'])
    duracao = timedelta(minutes=duracao_em_minutos)

    if data['data_inicial'].lower() == 'agora':
        data_inicial = datetime.now()
    else:
        data_inicial = datetime.now()
        data_inicial += timedelta(minutes=int(data['data_inicial']))

    pivo = PivoIrrigacao.objects.get(pk=data['pivo_id'])
    fazenda = Fazenda.objects.get(pk=data['fazenda_id'])
    evento = EventoIrrigacao.objects.create(pivo=pivo,
                                            fazenda=fazenda,
                                            duracao=duracao,
                                            data_hora_inicio=data_inicial)
    onOffPivo(request, pivo.token, evento.id)
    return JsonResponse({'id': evento.id}, status=201)


def deleteEvento(request, evento_id):
    evento = EventoIrrigacao.objects.get(pk=evento_id)
    evento.delete()
    return JsonResponse({}, status=204)


def updateEventoIrrigacao(request, id):
    data = json.loads(request.body)
    evento = EventoIrrigacao.objects.filter(id=id).update(status=data['status'])
    return JsonResponse({'id': evento.id}, status=201)


def getIrrigacaoEvento(request):
    fazenda_id = request.headers.get('fazendaId')
    fazenda = get_object_or_404(Fazenda, id=fazenda_id)

    queryset = EventoIrrigacao.objects.select_related('pivo').filter(fazenda=fazenda)

    eventos = [
        {
            'id': evento.id,
            'data_hora_inicio': evento.data_hora_inicio.strftime('%Y-%m-%d %H:%M:%S'),
            'duracao': int(evento.duracao.total_seconds() / 60),
            'status': evento.status,
            'pivo_id': evento.pivo.id,
            'pivo_nome': evento.pivo.nome,
        }
        for evento in queryset
    ]

    return JsonResponse({'response': eventos}, status=200)

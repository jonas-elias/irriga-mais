# from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework import status
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
    return JsonResponse({'id': fazenda.id}, status=status.HTTP_201_CREATED)


def loginFazenda(request):
    data = request.GET
    queryset = Fazenda.objects.filter(email=data['email']).all()

    if queryset.exists():
        fazenda = list(queryset.values())
        if (check_password(data['senha'], fazenda[0]['senha'])):
            token = secrets.token_hex(100 // 2)
            TokenAuth.objects.create(token=token, data_expiracao=timezone.now() + timezone.timedelta(days=1))
            return JsonResponse({'message': 'Autorizado!', 'token': token, 'id': fazenda[0]['id']}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({'message': 'Senha incorreta!'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return JsonResponse({'message': 'Não autorizado!'}, status=status.HTTP_401_UNAUTHORIZED)


def createPivo(request):
    data = request.GET
    token = secrets.token_hex(20 // 2)
    pivo = PivoIrrigacao.objects.create(nome=data['nome'], 
                                        descricao=data['descricao'],
                                        token=token,
                                        fazenda=Fazenda.objects.get(pk=data['fazenda_id']),
                                        tipo=data['tipo'])
    return JsonResponse({'id': pivo.id}, status=status.HTTP_201_CREATED)


def deletePivo(request, pivo_id):
    pivo = PivoIrrigacao.objects.get(pk=pivo_id)
    pivo.delete()
    return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


def getAllPivos(request):
    queryset = PivoIrrigacao.objects.all()
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
    evento = EventoIrrigacao.objects.create(pivo=pivo,
                                            duracao=duracao,
                                            data_hora_inicio=data_inicial)
    onOffPivo(request, pivo.token, evento.id)
    return JsonResponse({'id': evento.id}, status=status.HTTP_201_CREATED)


def deleteEvento(request, evento_id):
    evento = EventoIrrigacao.objects.get(pk=evento_id)
    evento.delete()
    return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


def updateEventoIrrigacao(request, id):
    data = json.loads(request.body)
    evento = EventoIrrigacao.objects.filter(id=id).update(status=data['status'])
    return JsonResponse({'id': evento.id}, status=status.HTTP_201_CREATED)


def getIrrigacaoEvento(request):
    queryset = EventoIrrigacao.objects.select_related('pivo').all()

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

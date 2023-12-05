from django.db import models

class Fazenda(models.Model):
    nome = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    senha = models.CharField(max_length=255)
    localizacao_latitude = models.FloatField()
    localizacao_longitude = models.FloatField()


class PivoIrrigacao(models.Model):
    nome = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    descricao = models.CharField(max_length=255)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class EventoIrrigacao(models.Model):
    pivo = models.ForeignKey(PivoIrrigacao, on_delete=models.CASCADE)
    data_hora_inicio = models.DateTimeField(auto_now_add=True)
    duracao = models.DurationField()
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('concluido', 'Concluído'),
        ('em_andamento', 'Em Andamento'),
        ('agendado', 'Agendado'),
        ('erro', 'Erro durante o processo'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado')

    def __str__(self):
        return f'Evento de Irrigação para {self.pivo} em {self.data_hora_evento}'


class TokenAuth(models.Model):
    token = models.CharField(max_length=255)
    data_expiracao = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.utils import timezone

class Conta(models.Model):
    nome = models.CharField(max_length=50) # Ex: Nubank, Carteira
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.nome

class Categoria(models.Model):
    TIPO_CHOICES = (
        ('R', 'Receita'),
        ('D', 'Despesa'),
        ('I', 'Investimento'),
    )
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    icone = models.CharField(max_length=20, default="💰", blank=True)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class SubCategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nome = models.CharField(max_length=50) # Ex: Açougue, Uber

    def __str__(self):
        return f"{self.categoria.nome} > {self.nome}"

class Cenario(models.Model):
    nome = models.CharField(max_length=50) # Ex: Planejamento 2026
    ativo = models.BooleanField(default=False) 

    def save(self, *args, **kwargs):
        # Garante que apenas um cenário esteja ativo por vez
        if self.ativo:
            Cenario.objects.filter(ativo=True).update(ativo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class MetaCategoria(models.Model):
    cenario = models.ForeignKey(Cenario, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    valor_planejado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cenario} - {self.categoria}: R$ {self.valor_planejado}"

class Transacao(models.Model):
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.now)
    descricao = models.CharField(max_length=255, blank=True, null=True)
    comprovante = models.FileField(upload_to='comprovantes/', null=True, blank=True)

    def __str__(self):
        return f"R$ {self.valor} - {self.subcategoria}"
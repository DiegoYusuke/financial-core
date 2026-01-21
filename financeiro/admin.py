from django.contrib import admin
from .models import Conta, Categoria, SubCategoria, Cenario, MetaCategoria, Transacao

@admin.register(SubCategoria)
class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria')
    list_filter = ('categoria',)

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    # ADICIONAMOS 'categoria' AQUI NA LISTA:
    list_display = ('id', 'data', 'descricao', 'valor', 'categoria', 'subcategoria', 'conta')
    
    # Adicionamos filtros laterais para facilitar sua vida
    list_filter = ('data', 'categoria', 'conta', 'categoria__tipo') 
    
    # Adicionamos barra de pesquisa (busca por descrição ou valor)
    search_fields = ('descricao', 'valor')
    
    # Isso coloca os links de data no topo para navegar rápido pelos meses
    date_hierarchy = 'data'

admin.site.register(Conta)
admin.site.register(Categoria)
admin.site.register(Cenario)
admin.site.register(MetaCategoria)
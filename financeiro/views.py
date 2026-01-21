from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from .models import Transacao, SubCategoria, Cenario, MetaCategoria, Categoria # <--- Importe Cenario e MetaCategoria
from .forms import TransacaoForm

def index(request):
    # 1. TOTAIS GERAIS (Cards do Topo)
    totais = Transacao.objects.aggregate(
        total_receita=Sum('valor', filter=Q(categoria__tipo='R')),
        total_despesa=Sum('valor', filter=Q(categoria__tipo='D')),
        total_invest=Sum('valor', filter=Q(categoria__tipo='I'))
    )
    receita = totais['total_receita'] or 0
    despesa = totais['total_despesa'] or 0
    investimento = totais['total_invest'] or 0
    saldo_total = receita - despesa - investimento

    # 2. GRÁFICO 1: PIZZA (Gastos por Categoria)
    despesas_por_categoria = Transacao.objects.filter(categoria__tipo='D').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
    grafico_labels = [item['categoria__nome'] for item in despesas_por_categoria]
    grafico_data = [float(item['total']) for item in despesas_por_categoria]

    # 3. GRÁFICO 2: BARRAS (Meta vs Realizado) - NOVIDADE AQUI
    # Vamos pegar o cenário ativo para comparar
    cenario_ativo = Cenario.objects.filter(ativo=True).first()
    
    bar_labels = []
    bar_meta = []
    bar_real = []

    # Pegamos todas as categorias de Despesa para comparar
    categorias_despesa = Categoria.objects.filter(tipo='D').order_by('nome')

    for cat in categorias_despesa:
        # Busca a meta (se não tiver, é 0)
        meta = MetaCategoria.objects.filter(cenario=cenario_ativo, categoria=cat).first()
        valor_meta = float(meta.valor_planejado) if meta else 0
        
        # Busca o gasto real (se não tiver, é 0)
        gasto_real = Transacao.objects.filter(categoria=cat).aggregate(Sum('valor'))['valor__sum'] or 0
        gasto_real = float(gasto_real)

        # Só adiciona no gráfico se tiver algum valor (pra não encher de barra vazia)
        if valor_meta > 0 or gasto_real > 0:
            bar_labels.append(cat.nome)
            bar_meta.append(valor_meta)
            bar_real.append(gasto_real)

    # 4. TABELA DE TRANSAÇÕES
    transacoes = Transacao.objects.all().order_by('-data')[:10]

    context = {
        'transacoes': transacoes,
        'saldo_total': saldo_total,
        'receita': receita,
        'despesa': despesa,
        
        # Dados da Pizza
        'grafico_labels': grafico_labels, 
        'grafico_data': grafico_data,

        # Dados das Barras (Novo)
        'bar_labels': bar_labels,
        'bar_meta': bar_meta,
        'bar_real': bar_real,
    }
    
    return render(request, 'financeiro/index.html', context)

def nova_transacao(request):
    if request.method == 'POST':
        form = TransacaoForm(request.POST)
        if form.is_valid():
            transacao = form.save(commit=False)
            
            # Correção para salvar a Categoria Principal também
            transacao.categoria = form.cleaned_data['categoria'] 
            
            transacao.save()
            return redirect('index')
    else:
        form = TransacaoForm()

    return render(request, 'financeiro/nova_transacao.html', {'form': form})

def load_subcategorias(request):
    categoria_id = request.GET.get('categoria')
    subcategorias = SubCategoria.objects.filter(categoria_id=categoria_id).order_by('nome')
    return render(request, 'financeiro/partials/subcategoria_options.html', {'subcategorias': subcategorias})

def planejamento(request):
    # 1. Pega ou cria o Cenário Padrão
    cenario, created = Cenario.objects.get_or_create(nome="Cenário Padrão", defaults={'ativo': True})

    # 2. Se o usuário clicou em SALVAR (POST)
    if request.method == 'POST':
        # Vamos varrer os dados que vieram do formulário
        for key, value in request.POST.items():
            if key.startswith('meta_'):
                # O nome do campo é "meta_5" (onde 5 é o ID da categoria)
                categoria_id = key.split('_')[1]
                valor = value.replace(',', '.') # Troca vírgula por ponto se precisar
                if valor == '': valor = 0
                
                # Salva ou Atualiza a Meta
                MetaCategoria.objects.update_or_create(
                    cenario=cenario,
                    categoria_id=categoria_id,
                    defaults={'valor_planejado': valor}
                )
        return redirect('planejamento')

    # 3. Preparar os dados para mostrar na tela (GET)
    categorias = Categoria.objects.all().order_by('tipo', 'nome')
    
    # Precisamos juntar a Categoria com sua Meta atual (se existir)
    dados_planejamento = []
    
    total_necessidade = 0 # Esse é o seu "Número Mágico"

    for cat in categorias:
        # Tenta pegar a meta salva, se não existir, retorna 0
        meta = MetaCategoria.objects.filter(cenario=cenario, categoria=cat).first()
        valor_meta = meta.valor_planejado if meta else 0
        
        # Se for Despesa ou Investimento, soma na necessidade de renda
        if cat.tipo in ['D', 'I']:
            total_necessidade += valor_meta

        dados_planejamento.append({
            'categoria': cat,
            'valor_meta': valor_meta
        })

    return render(request, 'financeiro/planejamento.html', {
        'dados': dados_planejamento,
        'total_necessidade': total_necessidade
    })
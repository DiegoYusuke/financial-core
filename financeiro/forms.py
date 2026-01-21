from django import forms
from .models import Transacao, SubCategoria

class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['data', 'valor', 'descricao', 'conta', 'categoria', 'subcategoria'] 
        # Nota: 'categoria' não existe direto em Transacao (é via subcategoria), 
        # mas vamos adicionar um campo extra no form para ajudar na seleção.

    # Campo extra apenas para o formulário (não salva no banco direto)
    categoria = forms.ModelChoiceField(
        queryset=None, # Vamos preencher na View
        empty_label="Selecione a Categoria",
        widget=forms.Select(attrs={
            'class': 'w-full p-2 border rounded',
            'hx-get': 'load-subcategorias/',  # <--- A MÁGICA DO HTMX AQUI
            'hx-target': '#id_subcategoria',  # Onde vai carregar o resultado
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Estilização manual rápida (Tailwind)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'w-full p-2 border rounded mb-4'})
        
        # Configurar o campo de data para ser um calendário
        self.fields['data'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded mb-4'})

        # Popular as categorias
        from .models import Categoria
        self.fields['categoria'].queryset = Categoria.objects.all()
        
        # Lógica do Dropdown vazio
        self.fields['subcategoria'].queryset = SubCategoria.objects.none()
        self.fields['subcategoria'].required = False

        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = SubCategoria.objects.filter(categoria_id=categoria_id)
            except (ValueError, TypeError):
                pass
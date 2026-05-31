# 📊 Matriz GUT - Priorização Estratégica

Uma aplicação interativa desenvolvida com **Streamlit** para análise e priorização de problemas e gargalos usando a metodologia GUT (Gravidade, Urgência, Tendência).

## 🎯 Funcionalidades

- ✅ Cadastro de problemas/gargalos
- ✅ Classificação por Gravidade, Urgência e Tendência (escala 1-5)
- ✅ Cálculo automático do Score GUT (G × U × T)
- ✅ Ordenação por prioridade
- ✅ Visualização em tabela interativa
- ✅ Gráfico de barras com escala de cores (verde)
- ✅ Gerenciamento de estado de sessão

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/rapharamone1987/RD.git
cd RD
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executar a Aplicação

```bash
streamlit run gut.py
```

A aplicação será aberta automaticamente no seu navegador (geralmente em `http://localhost:8501`).

## 📋 Como Usar

1. **Adicionar um Problema:**
   - Preencha a descrição do problema
   - Defina a Gravidade (1-5): 1 = Sem gravidade, 5 = Extremamente grave
   - Defina a Urgência (1-5): 1 = Pode esperar, 5 = Ação imediata
   - Defina a Tendência (1-5): 1 = Vai diminuir, 5 = Vai piorar rapidamente
   - Clique em "Adicionar Problema"

2. **Visualizar Resultados:**
   - A tabela mostra todos os problemas ordenados por score (maior prioridade no topo)
   - O gráfico de barras visualiza a criticidade de cada problema

## 🎨 Metodologia GUT

A Matriz GUT é uma ferramenta de priorização que calcula:

**Score GUT = Gravidade × Urgência × Tendência**

- **Gravidade (G):** Impacto do problema se não for resolvido
- **Urgência (U):** Tempo disponível para resolver o problema
- **Tendência (T):** Evolução do problema ao longo do tempo

Quanto maior o score, maior a prioridade.

## 📁 Estrutura do Projeto

```
RD/
├── gut.py                 # Aplicação Streamlit - Matriz GUT
├── app.py                 # Sua aplicação principal
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 🔧 Tecnologias Utilizadas

- **Streamlit** - Framework para criar apps web com Python
- **Pandas** - Manipulação de dados
- **Plotly** - Visualização interativa de gráficos

## 📝 Exemplos de Cenários

A aplicação vem com dados de simulação baseados em cenários comuns de administração:
- Atraso no inventário anual de bens móveis
- Inconsistência em relatórios de depreciação contábil
- Fluxo manual de requisição de materiais no SharePoint
- Falta de treinamento de novos servidores em conformidade

## 🚀 Deployment

### Streamlit Cloud (Recomendado)

1. Faça push do repositório para GitHub
2. Acesse [Streamlit Cloud](https://streamlit.io/cloud)
3. Conecte seu repositório GitHub
4. Selecione o branch e o arquivo `gut.py`
5. Deploy automático!

### Outros Serviços

A aplicação também pode ser deployada em:
- Heroku
- AWS
- Google Cloud
- Azure

## 📞 Suporte

Para dúvidas ou sugestões, abra uma [issue](https://github.com/rapharamone1987/RD/issues).

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

---

**Desenvolvido com ❤️ em Python**

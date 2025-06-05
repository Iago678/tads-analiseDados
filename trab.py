import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

df = pd.read_csv('sales.csv')


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Análise de Vendas de Jogos", className='text-center my-4')
        ], width=12)
    ]),
    
    # Filtros (funciona para todos os gráficos)
    dbc.Row([
        dbc.Col([
            html.Label("Selecione Gênero(s):", className='fw-bold'),
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': g, 'value': g} for g in df['Genre'].unique()],
                value=df['Genre'].unique().tolist(),
                multi=True,
                clearable=False,
                className='mb-4'
            )
        ], md=6),
        
        dbc.Col([
            html.Label("Selecione Plataforma(s):", className='fw-bold'),
            dcc.Dropdown(
                id='platform-dropdown',
                options=[{'label': p, 'value': p} for p in df['Platform'].unique()],
                value=df['Platform'].unique().tolist(),
                multi=True,
                clearable=False,
                className='mb-4'
            )
        ], md=6)
    ]),
    
    
    # Gráficos
    dbc.Row([
        dbc.Col(dcc.Graph(id='hist'), md=6),
        dbc.Col(dcc.Graph(id='scatter'), md=6),
    ], className='mb-4'),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='box'), md=6),
        dbc.Col(dcc.Graph(id='line'), md=6),
    ]),

    # Estatísticas
    dbc.Row([
        dbc.Col([
            html.Div(id='stats-container', className='p-3 bg-light border rounded')
        ], width=12)
    ], className='mb-4')

], fluid=True)

@callback(
    [Output('hist', 'figure'),
     Output('scatter', 'figure'),
     Output('box', 'figure'),
     Output('line', 'figure'),
     Output('stats-container', 'children')],
    [Input('genre-dropdown', 'value'),
     Input('platform-dropdown', 'value')]
)
def update_graphs(genre_select, plat_select):
    df_filtrado = filtrar_dados(df, genre_select, plat_select)
    stats = calcular_estatisticas(df_filtrado)
    
    # Gráficos
    hist = px.histogram(
        df_filtrado, x='Genre', y='Global_Sales', histfunc='sum',
        title='Vendas Globais por Gênero (em milhões)',
        labels={'Global_Sales': 'Vendas Globais (US$ milhões)', 'Genre': 'Gênero'},
        color='Genre'
    )
    
    scatter = px.scatter(
        df_filtrado, x='NA_Sales', y='EU_Sales', color='Genre', size='Global_Sales',
        title='Relação entre Vendas na América do Norte e Europa<br>(tamanho = vendas globais)',
        labels={'NA_Sales': 'Vendas América do Norte (US$ milhões)', 'EU_Sales': 'Vendas Europa (US$ milhões)'},
        hover_name='Name'
    )
    
    box = px.box(
        df_filtrado, x='Genre', y='Global_Sales',
        title='Distribuição de Vendas Globais por Gênero',
        labels={'Global_Sales': 'Vendas Globais (US$ milhões)', 'Genre': 'Gênero'},
        color='Genre',
        points='all'
    )
    
    line = px.line(
        df_filtrado.groupby('Year')['Global_Sales'].sum().reset_index(),
        x='Year', y='Global_Sales',
        title='Vendas Globais ao Longo dos Anos',
        labels={'Global_Sales': 'Vendas (US$ milhões)', 'Year': 'Ano'}
    )
    

    # Estatísticas da Tabela
    stats_comps = gerar_tabela(stats)
    
    return hist, scatter, box, line, stats_comps


def filtrar_dados(df, generos, plataformas):
    return df[(df['Genre'].isin(generos)) & (df['Platform'].isin(plataformas))]

def calcular_estatisticas(df_filtrado):
    correlacao = df_filtrado['NA_Sales'].corr(df_filtrado['EU_Sales'])
    
    if correlacao > 0.7:
        desc = 'forte e positiva'
    elif correlacao > 0.4:
        desc = 'moderada'
    else:
        desc = 'fraca ou inexistente'
    
    total = df_filtrado['Global_Sales'].sum()
    media = df_filtrado['Global_Sales'].mean()
    genero_top = df_filtrado.groupby('Genre')['Global_Sales'].sum().idxmax()
    plataforma_top = df_filtrado.groupby('Platform')['Global_Sales'].sum().idxmax()

    return {
        "correlacao": correlacao,
        "descricao_correlacao": desc,
        "total": total,
        "media": media,
        "genero_top": genero_top,
        "plataforma_top": plataforma_top
    }

def gerar_tabela(stats):
    return [
        html.H5("Estatísticas Descritivas", className='mb-3'),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Métrica"), html.Th("Valor")])),
            html.Tbody([
                html.Tr([html.Td("Correlação de vendas América do norte x Europa"), html.Td(f"{stats['correlacao']:.2f} ({stats['descricao_correlacao']})")]),
                html.Tr([html.Td("Vendas Globais Totais"), html.Td(f"US$ {stats['total']:,.2f} milhões")]),
                html.Tr([html.Td("Média de Vendas por Jogo"), html.Td(f"US$ {stats['media']:,.2f} milhões")]),
                html.Tr([html.Td("Gênero Mais Vendido"), html.Td(stats['genero_top'])]),
                html.Tr([html.Td("Plataforma Líder"), html.Td(stats['plataforma_top'])])
            ])
        ], bordered=True, striped=True)
    ]



if __name__ == '__main__':
    app.run(debug=True)
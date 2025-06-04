import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

# Carregar dados
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    # Filtros
    dbc.Row([
        dbc.Col([
            html.Label("Continente:"),
            dcc.Dropdown(
                id='continent-dropdown',
                options=[{'label': c, 'value': c} for c in df['continent'].unique()],
                value=['Asia', 'Europe', 'Americas'],
                multi=True
            )
        ], md=6),
    ]),
    
    # Gráficos
    dbc.Row([
        dbc.Col(dcc.Graph(id='hist'), md=6),
        dbc.Col(dcc.Graph(id='scatter'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='box'), md=6),
        dbc.Col(dcc.Graph(id='bar'), md=6),
    ])
])

@callback(
    [Output('hist', 'figure'),
     Output('scatter', 'figure'),
     Output('box', 'figure'),
     Output('bar', 'figure')],
    [Input('continent-dropdown', 'value')]
)
def update_graphs(selected_continents):
    filtered_df = df[df['continent'].isin(selected_continents)]

    # Histograma
    hist = px.histogram(filtered_df, x='continent', y='lifeExp', histfunc='avg')

    # Scatter
    scatter = px.scatter(filtered_df, x='gdpPercap', y='lifeExp', color='continent')

    # BoxPlot
    box = px.box(filtered_df, x='continent', y='gdpPercap')

    # Barras
    bar = px.bar(filtered_df, x='continent', y='gdpPercap', color='continent', barmode='group')

    return hist, scatter, box, bar

if __name__ == '__main__':
    app.run(debug=True)

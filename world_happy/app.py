import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Load the data
df = pd.read_csv('assets/2019.csv')

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the app
app.layout = dbc.Container([
    html.Div(className='app-header', children=[
        html.H1("World Happiness Index Dashboard", className='display-3')
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'Happiness Score', 'value': 'Score'},
                    {'label': 'GDP per Capita', 'value': 'GDP per capita'},
                    {'label': 'Social Support', 'value': 'Social support'},
                    {'label': 'Healthy Life Expectancy', 'value': 'Healthy life expectancy'},
                    {'label': 'Freedom to Make Life Choices', 'value': 'Freedom to make life choices'},
                    {'label': 'Generosity', 'value': 'Generosity'},
                    {'label': 'Perceptions of Corruption', 'value': 'Perceptions of corruption'},
                ],
                value='Score',
                style={'width': '100%'}
            )
        ], width={'size': 6, 'offset': 3}, className='dropdown-container')
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='world-map'), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='data-insights', className='data-insights'),
            html.Div(id='top-bottom-countries', className='top-bottom-countries')
        ], width=8),
        dbc.Col(html.Div(id='country-details', className='country-details'), width=4)
    ])
], fluid=True)

# Callback to update the map based on selected metric
@app.callback(
    Output('world-map', 'figure'),
    Input('metric-dropdown', 'value')
)
def update_map(selected_metric):
    fig = px.choropleth(
        df,
        locations="Country or region",
        locationmode='country names',
        color=selected_metric,
        hover_name="Country or region",
        color_continuous_scale=px.colors.sequential.Aggrnyl_r,
        title=f"World Happiness Index: {selected_metric}"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

# Callback to display data insights
@app.callback(
    Output('data-insights', 'children'),
    Input('metric-dropdown', 'value')
)
def update_insights(selected_metric):
    highest = df.loc[df[selected_metric].idxmax()]
    lowest = df.loc[df[selected_metric].idxmin()]
    insights = [
        html.H3(f"Highest {selected_metric}: {highest['Country or region']} ({highest[selected_metric]})"),
        html.H3(f"Lowest {selected_metric}: {lowest['Country or region']} ({lowest[selected_metric]})")
    ]
    return insights

# Callback to display top and bottom countries for the selected metric
@app.callback(
    Output('top-bottom-countries', 'children'),
    Input('metric-dropdown', 'value')
)
def update_top_bottom(selected_metric):
    top_countries = df.nlargest(5, selected_metric)
    bottom_countries = df.nsmallest(5, selected_metric)

    top_countries_list = html.Ul([html.Li(f"{row['Country or region']}: {row[selected_metric]}") for _, row in top_countries.iterrows()])
    bottom_countries_list = html.Ul([html.Li(f"{row['Country or region']}: {row[selected_metric]}") for _, row in bottom_countries.iterrows()])

    return html.Div([
        html.Div([
            html.H3("Top 5 Countries"),
            top_countries_list
        ], className='top-bottom-section'),
        html.Div([
            html.H3("Bottom 5 Countries"),
            bottom_countries_list
        ], className='top-bottom-section')
    ], className='top-bottom-container')

# Callback to display country details on map click
@app.callback(
    Output('country-details', 'children'),
    Input('world-map', 'clickData')
)
def display_country_details(clickData):
    if clickData:
        country_name = clickData['points'][0]['location']
        country_data = df[df['Country or region'] == country_name]

        if not country_data.empty:
            country = country_data.iloc[0]
            details = [
                html.H3(f"Details for {country_name}"),
                html.P(f"Overall Rank: {country['Overall rank']}"),
                html.P(f"Score: {country['Score']}"),
                html.P(f"GDP per Capita: {country['GDP per capita']}"),
                html.P(f"Social Support: {country['Social support']}"),
                html.P(f"Healthy Life Expectancy: {country['Healthy life expectancy']}"),
                html.P(f"Freedom to Make Life Choices: {country['Freedom to make life choices']}"),
                html.P(f"Generosity: {country['Generosity']}"),
                html.P(f"Perceptions of Corruption: {country['Perceptions of corruption']}")
            ]
            return html.Div(details, className='country-details-section')

    return html.Div("Click on a country to see details.", className='country-details-section')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 20:33:42 2021

@author: Jiwoo Ahn
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Import relevant libraries
import pandas as pd
import plotly.express as px

# Initiate the app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'AusCovidDash'

colors = {
    'background': '#000000',
    'text': '#5d76a9',
    'label': '#f5b112'
}

def plotInitial():
    # webscraping function inputs, manipulated url link (same as applying filter on website)
    
    df = {'Sold': [1269000], 'Land Size' : [683], 'Lattitude' : [-27.5269629], 'Longitude' : [153.0597635]}
    px.set_mapbox_access_token("pk.eyJ1Ijoiaml3b29haG4iLCJhIjoiY2wwNDE5bHR1MGRhZTNlcGRmcTY3OW9ibCJ9.8zwqW0ddcP_H8YsRwHlGhg")
    
    fig = px.scatter_mapbox(df, lat='Lattitude', lon='Longitude', color='Sold', size='Land Size',
                            color_continuous_scale=px.colors.sequential.Plasma, size_max=15, zoom=10)

    return fig
    
fig = plotInitial()

app.layout = html.Div([
    html.H1(children='Australia Property Map', style={'textAlign': 'center','font-family':'Verdana','color': colors['text'],'padding-top': 20}),
    html.Button('Scrape', id='update_button', n_clicks=0),
    dcc.Graph('dashboard', figure=fig,config={'displayModeBar': False})
    ])

@app.callback(
    Output('dashboard', 'figure'),
    [Input('update_button', 'n_clicks')],
)
def update_graph(n_clicks):
    fig = plotInitial()
    return fig

if __name__ == '__main__':
    app.run_server()
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

fig = px.scatter(x=[1, 2, 3], y=[4, 1, 2])

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
    #fig = plotInitial()
    fig = px.scatter(x=[1, 2, 3], y=[4, 1, 2])
    return fig

if __name__ == '__main__':
    app.run_server()
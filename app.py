# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 20:33:42 2021

@author: Jiwoo Ahn
"""

# Import relevant libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output , State
import plotly.express as px

import pandas as pd
from bs4 import BeautifulSoup
import time
import requests
from requests import get
import urllib.parse

# Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Property map'

class property():
    def __init__(self, state, suburb, property_type, beds, imax):
        self.state = state
        self.suburb = suburb
        self.property_type = property_type
        self.beds = beds
        self.imax = imax
        
    def latlong(self,address):
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
        response = requests.get(url).json()
        if len(response):
            lat,long = float(response[0]["lat"]), float(response[0]["lon"])
        else:
            lat,long = 'NA','NA'
        return lat, long
    
    def Scraper(self, page):
        # Lists for appending scraped data for later exporting
        ids = []
        urls = []
        addresses = []
        prices= []
        prices_date = []
        last_prices = []
        last_prices_date = []
        rents = []
        rents_date = []
        bedrooms = []
        bathrooms = []
        carparks = []
        landsizes = []
        buildingsizes = []
        agents = []
        lats = []
        longs = []
        
        # house.speakingsame.com url 
        headers = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                              'AppleWebKit/537.36 (KHTML, like Gecko)'
                              'Chrome/45.0.2454.101 Safari/537.36'),
                              'referer': 'http://house.speakingsame.com/'}
        
        url = f'http://house.speakingsame.com/p.php?q={self.suburb.replace(" ","+")}&p={page}&s=1&st=&type={self.property_type}&count=300&region={self.suburb.replace(" ","+")}&lat=0&lng=0&sta={self.state}&htype=&agent=0&minprice=0&maxprice=0&minbed={self.beds}&maxbed={self.beds}&minland=0&maxland=0'
        print(url)
        
        time.sleep(3)
        response = get(url, headers=headers)

        # parse html page from reponse to text using bs4 library
        html_soup = BeautifulSoup(response.text, 'html.parser')
        
        # find all classes called 'addr', which contains the address and property url
        # Then loop through these classes and extract info into lists for later exporting
        addr_containers = html_soup.find_all('span', {'class' : 'addr'})
        for addr in addr_containers:
            children = addr.findChildren("a" , recursive=False)
            url_temp = children[0].attrs['href']
            urls.append('http://house.speakingsame.com/' + url_temp)
            addresses.append(addr.text)
            ids.append(url_temp.split('&')[2][3:])
            
            address = f'{addr.text}, {self.suburb}, {self.state}, Australia'
            address_ = address
            print(address)
            idx = address.find('/')
            if idx >= 0:
                address_ = address[idx+1:]            
            lat, long = self.latlong(address_)
            lats.append(lat)
            longs.append(long)
                        
        for listing_id in ids:
            price = ''
            price_date = ''
            last_price = ''
            last_price_date = ''
            rent = ''
            rent_date = ''
            bedroom = ''
            bathroom = ''
            carpark = ''
            landsize = ''
            buildingsize = ''
            agent = ''
            
            table = html_soup.find('table', id='r'+listing_id)
            rows = table.find_all('td')[4:]
            for row in rows:
                rtext = row.text.split()
                if len(rtext) > 1:
                    if rtext[0] == 'Sold' and rtext[4].isnumeric():
                        try:
                            price = float(rtext[1].replace('$','').replace(',',''))
                        except:
                            price = 'NA'
                        price_date = rtext[3] + ' ' + rtext[4]
                    if rtext[0] == 'Last' and rtext[1] == 'Sold':
                        last_price = rtext[2]
                        last_price_date = rtext[4] + ' ' + rtext[5]
                    if rtext[0] == 'Rent':
                        rent = rtext[1]
                        rent_date = rtext[3] + ' ' + rtext[4]
                    if rtext[0] == f'{self.property_type}:':
                        if len(rtext) > 1:
                            bedroom = rtext[1]
                        if len(rtext) > 2:
                            bathroom = rtext[2]
                        if len(rtext) > 3:
                            carpark = rtext[3]
                    if rtext[0] == 'Land' and rtext[1] == 'size:':
                        try:
                            landsize = float(rtext[2].replace(',',''))
                        except:
                            landsize = 'NA'
                        if len(row.find_all('b')) > 1 and rtext[5] == 'Building' and rtext[6] == 'size:':
                            buildingsize = rtext[7]
                    if rtext[0] == 'Agent:':
                        agent = row.text.split(':')[1]
            
            if self.property_type == 'House':
                if landsize == "":
                    landsize = 'NA'
                                
            try:
                bathroom = float(bathroom)
            except:
                bathroom = 'NA'
                
            prices.append(price)
            prices_date.append(price_date)
            last_prices.append(last_price)
            last_prices_date.append(last_price_date)
            rents.append(rent)
            rents_date.append(rent_date)
            bedrooms.append(bedroom)
            bathrooms.append(bathroom)
            carparks.append(carpark)
            landsizes.append(landsize)
            buildingsizes.append(buildingsize)
            agents.append(agent)
            
                
        df = pd.DataFrame({#'Property Id': ids,
                            #'Website URL': urls,
                            'Address': addresses,
                            'Sold': prices,
                            'Sold Date': prices_date,
                            'Selling Agent': agents,
                            'Last Sold': last_prices,
                            'Last Sold Date': last_prices_date,
                            'Bedrooms': bedrooms,
                            'Bathrooms': bathrooms,
                            'Carparks': carparks,
                            'Land Size': landsizes,
                        'Building Size': buildingsizes,
                        'Lattitude' : lats,
                        'Longitude' : longs})
        return df

    def Database(self):
        df = self.Scraper(0)
        for i in range(1,self.imax):
            df_i = self.Scraper(i)
            df = df.append(df_i)
        
        return df
    
def plot(State, suburb, property_type, beds, imax):
    # webscraping function inputs, manipulated url link (same as applying filter on website)

    df = download(State, suburb, property_type, beds, imax)
    
    px.set_mapbox_access_token("pk.eyJ1Ijoiaml3b29haG4iLCJhIjoiY2wwNDE5bHR1MGRhZTNlcGRmcTY3OW9ibCJ9.8zwqW0ddcP_H8YsRwHlGhg")
    
    if property_type == 'House':
        fig = px.scatter_mapbox(df, lat='Lattitude', lon='Longitude', color='Sold', size='Land Size',
                                hover_name='Address',
                                hover_data=['Sold Date','Bathrooms'],
                                color_continuous_scale=px.colors.sequential.Plasma, size_max=15, zoom=12)
    else:
        fig = px.scatter_mapbox(df, lat='Lattitude', lon='Longitude', color='Sold', size='Bathrooms',
                                hover_name='Address',
                                hover_data=['Sold Date', 'Land Size'],
                                color_continuous_scale=px.colors.sequential.Plasma, size_max=15, zoom=10)
    return fig

def download(State, suburb, property_type, beds, imax):
    # webscraping function inputs, manipulated url link (same as applying filter on website)

    property_object = property(State.lower(),suburb,property_type,beds, imax)
    
    df = property_object.Database()
    
    df = df[df['Sold'] != "NA"]
    df = df[df['Land Size'] != "NA"]
    df = df[df['Bathrooms'] != "NA"]
    df = df[df['Lattitude'] != "NA"]
    df = df[df['Longitude'] != "NA"]
    
    return df

def plotInitial():
    # webscraping function inputs, manipulated url link (same as applying filter on website)
    
    df = {'Sold': [1269000], 'Land Size' : [683], 'Lattitude' : [-27.5269629], 'Longitude' : [153.0597635]}
    px.set_mapbox_access_token("pk.eyJ1Ijoiaml3b29haG4iLCJhIjoiY2wwNDE5bHR1MGRhZTNlcGRmcTY3OW9ibCJ9.8zwqW0ddcP_H8YsRwHlGhg")
    
    fig = px.scatter_mapbox(df, lat='Lattitude', lon='Longitude', color='Sold', size='Land Size',
                            color_continuous_scale=px.colors.sequential.Plasma, size_max=15, zoom=10)

    return fig


# DASH APP CONFIGURATION
aus_states = ['QLD','NSW','VIC','WA','SA', 'TAS', 'ACT']
props = ['House','Townhouse','Unit']
numb = [10,20,30,40,50,60,70,80,90,100]

styledict = {'display':'inline-block','vertical-align':'left', 'margin-top':'10px','margin-left':'20px','font-size':10,'font-family':'Verdana','textAlign':'center'}

# Dropdown and input fields, saved as variables
state = dcc.Dropdown(id='state-state', options=[{'label': i, 'value': i} for i in aus_states], value='QLD', style={'width': '60px', 'display':'inline-block', 'margin-left':'5px','vertical-align':'middle'})

suburb = dcc.Input(id='suburb-state', type='text', value='Holland Park', style={'width': '150px', 'display':'inline-block', 'margin-left':'5px','vertical-align':'left', 'textAlign' : 'center'})

property_type = dcc.Dropdown(id='property_type-state', options=[{'label': i, 'value': i} for i in props], value='House', style={'width': '80px', 'display':'inline-block', 'margin-left':'5px','vertical-align':'middle'})

beds = dcc.Input(id='beds-state', type='number', value=4, min=1, max=6, style={'width': '60px', 'display':'inline-block', 'margin-left':'5px','vertical-align':'left', 'textAlign':'center',})

numb = dcc.Dropdown(id='numb-state', options=[{'label': i, 'value': i} for i in numb], value=20, style={'width': '80px', 'display':'inline-block', 'margin-left':'5px','vertical-align':'middle','textAlign':'center',})

fig = plotInitial()

# App HTML layout
app.layout = html.Div([    
    html.Div([html.Img(src='https://raw.githubusercontent.com/j-ahn/PropertyMap/main/favicon.png',style={'display':'inline-block', 'width': '1.5%', 'height': '1.5%', 'margin-left': '25px'}),
              html.H1(children='Australian Property Price Map',
            style={'display':'inline-block','textAlign': 'left','margin-left': '25px', 'font-family':'Verdana', 'font-size': 30,'vertical-align':'middle'})],
             style={'margin-top': '25px'}),

    html.Br(style={'height':'10px'}),
    
    html.Div([html.Label(["State:",state])],
         style=styledict),
    
    html.Div([html.Label(["Suburb:",suburb])],
         style=styledict),
    
    html.Div([html.Label(["Property Type:",property_type])],
         style=styledict),
        
    html.Div([html.Label(["Bedrooms:",beds])],
         style=styledict),
    
    html.Div([html.Label(["Number of properties:",numb])],
         style=styledict),
        
    html.Div([html.Button('Scrape', id='update_button', n_clicks=0)], style=styledict),
    
    dcc.Loading(
        id="loading",
        children=[html.Div([dcc.Graph('dashboard', style={"height":'75vh'}, config={'displayModeBar': True})])],
        type="circle"
        ),
    
        html.Div(dcc.Markdown('''This tool web-scrapes propery sale data and presents them spatially. The colours represents the sale price, while the radius of the bubble represents the land size or bathrooms (houses vs. townhouses & units).
       
    Created by : Jiwoo Ahn
    
    [Github Repo](https://github.com/j-ahn/propertymap)
    
    '''), style = {'font-size':10,'font-family':'Verdana','textAlign':'center'})
])

@app.callback(
    Output('dashboard', 'figure'),
    Input('update_button', 'n_clicks'),
    State('state-state', 'value'),
    State('suburb-state', 'value'),
    State('property_type-state', 'value'),
    State('beds-state', 'value'),
    State('numb-state', 'value'),
)

def update_graph(n_clicks, state, suburb, property_type, beds, numb):
    if n_clicks == 0:
        fig = plotInitial()
    else:
        fig = plot(state,suburb,property_type,beds, int(numb*0.1))
    return fig

if __name__ == '__main__':
    app.run_server()
# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import pandas as pd
import numpy as np
import plotly
import DBAccessor as dbac
import plotly.graph_objs as go

query = """WITH TRIP AS(
	SELECT TRIPS_Doppler.TRIP_ID AS TRIP_ID_Doppler, TRIPS_LINKS_LOOKUP2.TRIP_ID AS TRIP_ID_Normal
	FROM TRIPS_Doppler,TRIPS_LINKS_LOOKUP2
	WHERE TRIPS_Doppler.SENSOR_ID = TRIPS_LINKS_LOOKUP2.SENSOR_ID
	AND TRIPS_Doppler.START_TIME = TRIPS_LINKS_LOOKUP2.START_TIME
	AND TRIPS_Doppler.END_TIME = TRIPS_LINKS_LOOKUP2.END_TIME)
,Doppler AS(
	SELECT TRIP.TRIP_ID_Doppler, COUNT(*) as DopplerCount
	FROM TRIP, ECOLOG_Doppler
	WHERE TRIP.TRIP_ID_Doppler = ECOLOG_Doppler.TRIP_ID
	GROUP BY TRIP.TRIP_ID_Doppler)
,Normal as(
	SELECT TRIP.TRIP_ID_Normal, COUNT(*) as NormalCount
	FROM TRIP, ECOLOG_LINKS_LOOKUP2
	WHERE TRIP.TRIP_ID_Normal = ECOLOG_LINKS_LOOKUP2.TRIP_ID
	GROUP BY TRIP.TRIP_ID_Normal)

SELECT TRIP.TRIP_ID_Doppler, TRIP.TRIP_ID_Normal, DopplerCount, NormalCount
FROM TRIP,Doppler,Normal
WHERE TRIP.TRIP_ID_Doppler = Doppler.TRIP_ID_Doppler
AND TRIP.TRIP_ID_Normal = Normal.TRIP_ID_Normal
"""

df = dbac.DBAccessor.ExecuteQueryDF(query)

app = dash.Dash(__name__)
server = app.server

#app.css.config.serve_locally = True
#app.scripts.config.serve_locally = True

my_css_url = "https://codepen.io/chriddyp/pen/bWLwgP.css"
app.css.append_css({
    "external_url": my_css_url
})


#DF_GAPMINDER = pd.read_csv(
#    'https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv'
#)
DF_GAPMINDER = df

available_indicators = df.columns

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='DopplerCount'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='NormalCount'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            #hoverData={'points': [{'customdata': 'Japan'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),

])

@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-xaxis-type', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-type', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type):

    return {
        'data': [go.Scatter(
            x=df[xaxis_column_name],
            y=df[yaxis_column_name],
            text=df['TRIP_ID_Normal'],
            customdata=df['TRIP_ID_Normal'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 50, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(host = '0.0.0.0')
    #app.debug = True
    #app.run(host='0.0.0.0')
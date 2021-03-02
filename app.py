# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import pandas as pd
import numpy as np
import altair as alt
from altair_saver import save
alt.renderers.enable('mimetype')
alt.data_transformers.enable('data_server')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options



game = pd.read_csv("vgsales.csv")

game.Year = game.Year.astype("Int64")
print(nulls.groupby("Year").size())
print(nulls.groupby("Genre").size())
print(nulls.groupby("Platform").size())

#For the analysis of sales - melting the NA,EU,JP,Other and Total columns
game_melt = game.melt(id_vars=["Rank", "Name","Platform","Year","Genre","Publisher"], 
        var_name="Region", 
        value_name="Sales").reset_index(drop=True)

sorted_genre_count = list(game.groupby("Genre").size().sort_values(ascending=False).index)
sorted_year_count = list(game.groupby("Year").size().sort_values(ascending=False).index)
sorted_platform_count = list(game.groupby("Platform").size().sort_values(ascending=False).index)

genre_count = alt.Chart(game).mark_bar().encode(
    alt.X("Genre",type="nominal",sort=sorted_genre_count),
    alt.Y("count()",title="Number of games",type="quantitative"),
    alt.Color("count()",scale=alt.Scale(scheme='category20b'),legend=None),
    alt.Tooltip("count()"))



app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=genre_count
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
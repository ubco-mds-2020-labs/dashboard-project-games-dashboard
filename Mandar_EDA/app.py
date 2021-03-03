
import altair as alt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from vega_datasets import data
import pandas as pd
import numpy as np
from altair_saver import save




game = pd.read_csv("vgsales.csv")
    

nulls = game[game.isna().any(axis=1)] #List of games with nulls in any field 
game.sort_values("Name").loc[game.Name.isin(game.Name[game.Name.duplicated()]),["Name","Platform"]].head(15) #Game titles that show up on multiple platforms 
game_melt = game.melt(id_vars=["Rank", "Name","Platform","Year","Genre","Publisher"], 
        var_name="Region", 
        value_name="Sales").reset_index(drop=True)

genre_data = pd.Series(game.groupby(['Year','Genre']).size().groupby('Year').size(), name='Genre')
pub_data = pd.Series(game.groupby(['Year','Publisher']).size().groupby('Year').size(), name='Publisher')
plat_data = pd.Series(game.groupby(['Year','Platform']).size().groupby('Year').size(), name='Platform')
rel_data = pd.concat([genre_data,pub_data,plat_data], axis=1).reset_index()



def plot_altair(xmax=2015):
    chart = alt.Chart(rel_data[rel_data['Year'] < xmax]).transform_fold(['Genre','Publisher','Platform']
).mark_bar(point=True).encode(
    x='Year:O',
    y=alt.Y('value:Q', axis=alt.Axis(title='Number of Genre/Publishers/Platforms')),
    color=alt.Color('key:N', legend=alt.Legend(title='Feature'))
).properties(width=1000)
    return chart.to_html()

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app = dash.Dash(__name__)
app.layout = html.Div([
        html.Iframe(id='plot1',
            srcDoc=plot_altair(),style={'border-width': '0', 'width': '100%', 'height': '400px'}),dcc.Slider(id='xslider', min=1980, max=2020, value = 2015, marks={1980: '1980', 1990: '1990', 2000: '2000', 2010: '2010', 2020: '2020'})])

@app.callback(
    Output('plot1', 'srcDoc'),
    Input('xslider', 'value'))
def update_output(xmax):
    return plot_altair(xmax)

if __name__ == '__main__':
    app.run_server(debug=True, port = 8051) 


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






app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app = dash.Dash(__name__)



app.layout = html.Div([html.Iframe(id = 'plot1',style={'border-width': '0', 'width': '100%', 'height': '400px'}),dcc.RangeSlider(id='xslider', min=1980, max=2020, value=[1980, 2015], marks={1980: '1980', 1985: '1985', 1990: '1990', 1995: '1995', 2000: '2000', 2005: '2005', 2010: '2010', 2015: '2015', 2020: '2020'}),
    dcc.Dropdown(id = 'dropdown', value = 'GP1',
        options=[
            {'label': 'Genre + Platform + Publisher', 'value':'GP1'},
            {'label': 'Genre + Platform', 'value': 'GP2'},
            {'label': 'Genre + Publisher', 'value': 'GP3'},
            {'label': 'Platform + Publisher', 'value': 'GP4'},
            {'label': 'Genre', 'value': 'GP5'},
            {'label': 'Platform', 'value': 'GP6'},
            {'label': 'Publisher', 'value': 'GP7'}
        ],
            placeholder='Genre+Platform+Publisher...')])


@app.callback(
    Output('plot1', 'srcDoc'),
    Input('xslider','value'),
    Input('dropdown','value'))
def plot_altair(value=[1980, 2020],value1='GP1'):
    xmin = value[0]
    xmax = value[1]
    drop_down = value1
    title_plot='Number of Genre/Publishers/Platforms'
    var1 = ['Genre','Publisher','Platform']
    if value1 == 'GP1':
        var1 = ['Genre','Publisher','Platform']
        title_plot='Number of Genre/Publishers/Platform'
    if value1 == 'GP2':
        var1 = ['Genre','Platform']
        title_plot='Number of Genre/Platform'
    if value1 == 'GP3':
        var1 = ['Genre','Publisher']
        title_plot='Number of Genre/Publisher'
    if value1 == 'GP4':
        var1 = ['Platform','Publisher']
        title_plot='Number of Platform/Publisher'
    if value1 == 'GP5':
        var1 = ['Genre']
        title_plot='Number of Genre'
    if value1 == 'GP6':
        var1 = ['Publisher']
        title_plot='Number of Publisher'
    if value1 == 'GP7':
        var1 = ['Platform']
        title_plot='Number of Platform'
    
    
    chart = alt.Chart(rel_data[(rel_data['Year'] < xmax) & (rel_data['Year'] > xmin)]).transform_fold(var1
).mark_bar(point=True).encode(
    x='Year:O',
    y=alt.Y('value:Q', axis=alt.Axis(title=title_plot)),
    color=alt.Color('key:N', legend=alt.Legend(title='Feature'))
).properties(width=1000)
    return chart.to_html()




if __name__ == '__main__':
    app.run_server(debug=True, port = 8051) 
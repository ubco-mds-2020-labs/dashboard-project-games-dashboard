#Dash components
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, Output

#Graphing components
import altair as alt
import pandas as pd
alt.data_transformers.disable_max_rows() #Disable max rows

#Read in data & basic wrangling 
game = pd.read_csv("data/vgsales.csv")
game.Year = game.Year.astype("Int64")
game_melt = game.melt(id_vars=["Rank", "Name","Platform","Year","Genre","Publisher"], var_name="Region", value_name="Sales").reset_index(drop=True)
sales_data = game_melt.loc[game_melt.Region != "Global_Sales",:]
sorted_genre_totalsales = list(game.groupby("Genre").sum().sort_values("Global_Sales",ascending=False).index)

#Initialize app
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#Side Bar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
sidebar = html.Div(
    [
        html.H1("Game Protoype", className="display-4"),
        html.Hr(),
        html.P("Filters for graphs and tables", className="lead"),
        html.P("Region Dropdown"),
        dcc.Dropdown(
            id="region_filter",
            value='NA_Sales',  # REQUIRED to show the plot on the first page load
            options=[{'label': regions, 'value': regions} for regions in list(sales_data.Region.unique())]
            ),
        html.P("Table size"),
        dcc.RadioItems(
            id="table_display",
            options = [{"label":"5","value":5},
                {"label":"10","value":10},
                {"label":"15","value":15},
                {"label":"20","value":20}],
            value = 5,
            labelStyle={'display': 'block'}
        ),
    ],
    style=SIDEBAR_STYLE,
)

#Main Body
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
content = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Iframe(
                id = "titles_graph",
                style={'border-width': '1', 'width': '400px', 'height': '450px'}
            )
        ),
        dbc.Col(
            dash_table.DataTable(
                id = "datatable",
                columns = [{"name":i , "id":i} for i in sales_data.columns],
                data = sales_data.loc[0:5,].to_dict("records")
            )
        )    
    ])
    ],
    style = CONTENT_STYLE
)

#Putting together Sidebar + Main Body
app.layout = dbc.Container([sidebar,content])

#Call back for table
@app.callback(
    Output("datatable","data"), #Output to ID: datatable for value:data
    Input("region_filter","value"),
    Input("table_display","value"))
def update_table(region_filter,n):
    filtered_data = sales_data[sales_data.Region==region_filter].sort_values("Sales",ascending=False)[0:n]
    return filtered_data.to_dict("records")


#Call back for Graph 1: Region Sales + Title Name
@app.callback(
    Output("titles_graph","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def title_plot(region_filter):
    sorted_genre = list(sales_data[sales_data.Region==region_filter].groupby("Genre").sum().sort_values("Sales",ascending=False).index)  
    chart=alt.Chart(sales_data[sales_data.Region==region_filter]).mark_circle(size=50).encode(
        alt.X("Genre",sort=sorted_genre,title=None),
        alt.Y("Sales:Q",stack=None, title="Sales (in millions)"),
        alt.Color("Genre",scale=alt.Scale(scheme='category20')),
        alt.Tooltip("Name"))
    chart = chart + alt.Chart(sales_data[sales_data.Region==region_filter].sort_values("Sales",ascending=False).iloc[:5,]).mark_text(align = "left", dx=10).encode(
        alt.X("Genre",sort=sorted_genre),
        alt.Y("Sales:Q"),
        text="Name").properties(title=region_filter)
    return chart.to_html()

#Call back for Table 


#Convention
if __name__ == '__main__':
    app.run_server(debug=True)


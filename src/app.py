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
game = pd.read_csv("../data/vgsales.csv")           # Modified (by Aamir)

game.Year = game.Year.astype("Int64")
game_melt = game.melt(id_vars=["Rank", "Name","Platform","Year","Genre","Publisher"], var_name="Region", value_name="Sales").reset_index(drop=True)
sales_data = game_melt.loc[game_melt.Region != "Global_Sales",:]
sorted_genre_totalsales = list(game.groupby("Genre").sum().sort_values("Global_Sales",ascending=False).index)

#Global Variables (by Aamir)
regions = {"NA_Sales": "North America", "EU_Sales": "Europe", "JP_Sales": "Japan", "Other_Sales": "Others"}

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
    ]),
    dbc.Row([   # Middle graphs (by Aamir)
        dbc.Col(
            html.Iframe(
                id = "releases_graph",
                style={'border-width': '1', 'width': '450px', 'height': '500px'}
            )
        ),
        dbc.Col(
            html.Iframe(
                id = "sales_graph",
                style={'border-width': '1', 'width': '450px', 'height': '500px'}
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


####################################################################################################
# Aamir Code
#Call back for Graph Middle 1: Region Releases + Title Name
@app.callback(
    Output("releases_graph","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def title_plot(region_filter):
    #2) Lets look at sales across Genres for each Region
    #Genres are sorted by decreasing Global Sales (Action is most sales vs Strategy is least)
    #Notice we see Shooters - while having fewer games released, still sold a lot of copies meaning their titles seemed to do well and the same (to a larger extent) can be said about Platformers.
    #Looking at the means of each genre, we can see exacly as we noticed above with the mean number of sales in the Shooter/Platform genre now ahead of the rest. 
    #It is also interesting to see the trend across genres. We see NA, EU and Other sale patters tend to be more similar while JP sale patterns are distinct from the other regions, with a large emphasis on RPG, Platformers. 
    sales_data = game_melt.loc[game_melt.Region != region_filter,:]
    sorted_genre_totalsales = list(game.groupby("Genre").sum().sort_values(region_filter,ascending=False).index)

    genre_sales = alt.Chart(sales_data).mark_bar(opacity=0.5).encode(
        alt.X("Genre",type="nominal",sort=sorted_genre_totalsales),
        alt.Y("sum(Sales)",title="Total Number of Sales (in millions)",type="quantitative",stack=None)#,
        #alt.Color("Region",scale=alt.Scale(scheme='set1'),type="nominal"),
        #alt.Tooltip("Region")
        )
    genre_sales = genre_sales+genre_sales.mark_circle()

    genre_plots = (genre_sales).properties(title={"text":["Distribution of Sales in", regions[region_filter]]}).configure_axis(
                    labelFontSize=12,
                    titleFontSize=13).configure_title(fontSize = 25,subtitleFontSize=15) 
    return genre_plots.to_html()




#Call back for Graph Middle 1: Region Releases + Title Name
@app.callback(
    Output("sales_graph","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def title_plot(region_filter):
    #1) Basic Exploratory visualisations of things we noted in the Initial Thoughts
    #Counts of number of games in each genre, platform and number of games released in each year
    #Genre and Platform counts are coloured by number of counts and sorted from largest to smallest
    #Year counts are coloured by year and sorted from largest to smallest 
    sorted_genre_count = list(game.groupby("Genre").size().sort_values(ascending=False).index)
    sorted_year_count = list(game.groupby("Year").size().sort_values(ascending=False).index)
    sorted_platform_count = list(game.groupby("Platform").size().sort_values(ascending=False).index)

    genre_count = alt.Chart(game).mark_bar().encode(
        alt.X("Genre",type="nominal",sort=sorted_genre_count),
        alt.Y("count()",title="Number of games",type="quantitative"))

    genre_count = genre_count.properties(title={"text": ["Distribution of Releases in", regions[region_filter]], 
    }).configure_title(fontSize = 25,subtitleFontSize=15)
    return genre_count.to_html()

####################################################################################################


#Convention
if __name__ == '__main__':
    app.run_server(debug=True)


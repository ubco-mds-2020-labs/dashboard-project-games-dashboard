#Dash components
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

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

#Data wrangling 
sales_data = game_melt.loc[game_melt.Region != "Global_Sales",:]
sales_data_platform = sales_data.groupby(["Platform","Year","Genre","Region"]).sum().reset_index()[["Platform","Year","Genre","Region","Sales"]]
sales_data_publisher = sales_data.groupby(["Publisher","Year","Genre","Region"]).sum().reset_index()[["Publisher","Year","Genre","Region","Sales"]]

#Global variables
regions = {"NA_Sales": "North America", "EU_Sales": "Europe", "JP_Sales": "Japan", "Other_Sales": "Other Regions"}

#Initialize app
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

###Styling
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "padding": "0.5rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "16.5rem",
    "margin-right": "2rem",
    "width":"82.5%",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
}


###Cards
card_graph_tab1 = dbc.Card(
    [
    dbc.CardBody(
        [
            dbc.Row([html.H4("Number of copies released", className="card-title")]),
            dbc.Row([html.P("Dessagregation per platform, publisher and genre",className="card-text")]),
            dbc.Row([
            html.Iframe(
                id = "region_releases",
                style={'border-width': '0', 'width': '450px', 'height': '450px'}
            )
            ]),
            dbc.Row([
            html.Iframe(
                id = "time_sales",
                style={'border-width': '0', 'width': '1000px', 'height': '450px'}
            )
            ])
        ]
    ),
    ],
    style={"width": "auto"},
)

card_graph_tab2 = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([html.H4("Number of copies sold", className="card-title")]),
            dbc.Row([html.P("Dessagregation per platform, publisher and genre",className="card-text")]),
            dbc.Row([
            html.Iframe(
                id = "region_sales",
                style={'border-width': '0', 'width': '450px', 'height': '450px'}
            )
            ]),
            dbc.Row([
            html.Iframe(
                id = "time_releases",
                style={'border-width': '0', 'width': '1000px', 'height': '450px'}
            )
            ])
        ]
    ),
)

card_graph_tab3 = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row([html.H4("Top Game titles, Platforms and Publishers across Genres", className="card-title")]),
            dbc.Row([html.P("Video game titles with detailed information",className="card-text")]),
            dbc.Row([
            html.Iframe(
                id = "title_perf_graph",
                style={'border-width': '0', 'width': '450px', 'height': '450px'}
            ),
            html.Iframe(
                id = "platform_perf_graph",
                style={'border-width': '0', 'width': '450px', 'height': '450px'}
            ),
            html.Iframe(
                id = "publisher_perf_graph",
                style={'border-width': '0', 'width': '450px', 'height': '450px'}
            )
            ])
        ]
    ),
)
card_table = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Table of the top Game Titles", className="card-title"),
            html.P("Stuff below",className="card-text"),
            dash_table.DataTable(
                id = "datatable",
                columns = [{"name": "Global Ranking" , "id":"Rank"},
                           {"name": "Game Title" , "id": "Name"},
                           {"name": "Platform" , "id":"Platform"},
                           {"name": "Release Year" , "id": "Year"},
                           {"name": "Genre" , "id": "Genre"},
                           {"name": "Publisher" , "id": "Publisher"},
                           {"name": "Sales (in millions)" , "id": "Sales"}],
                data = sales_data.loc[0:5,].to_dict("records"),
                css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                style_cell={
                    "whiteSpace":"normal",
                    "height":"auto",
                    "width": '{}%'.format(len(["Rank","Name","Year","Genre","Platform","Publisher","Sales"]))
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ["Rank","Name","Year","Genre","Platform","Publisher"]
                ],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
        ]
    ),
)

###Formatting page
#
#Sidebar 
sidebar = html.Div(
    [
        html.H1("Game Protoype", className="display-4"),
        html.Hr(),
        html.P("Filters for graphs and tables", className="lead"),
        html.P("Region Dropdown"),
        dcc.Dropdown(
            id="region_filter",
            value='NA_Sales',  # REQUIRED to show the plot on the first page load
            options=[{'label': "North America", 'value': "NA_Sales"},
                     {'label': "Europe", 'value': "EU_Sales"},
                     {'label': "Japan", 'value': "JP_Sales"},
                     {'label': "Other", 'value': "Other_Sales"},]
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
#Tab Styles
tabs_styles = {
    'height': '44px',
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '1px'
}
#Main Body
content = html.Div([
    html.H3("Change the metrics:"),
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Number of games released', value='tab-1', style = tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Number of copies sold', value='tab-2', style = tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Top titles', value='tab-3', style = tab_style, selected_style=tab_selected_style),
    ],style=tabs_styles), 
    html.Div(id='tabs-content')
    ],
    style=CONTENT_STYLE
)
#Putting together Sidebar + Main Body
app.layout = html.Div([
        sidebar,
        content 
])

###Callbacks 
#
#Call back for Tabs
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
                    dbc.Container([
                    dbc.Row([card_graph_tab1])
                    ],style={'margin-left': '0'})
        ])
    elif tab == 'tab-2':
        return html.Div([
                    dbc.Container([
                    dbc.Row([card_graph_tab2])
                    ],style={'margin-left': '0'})
        ])
    elif tab == 'tab-3':
        return html.Div([
                    dbc.Container([
                        dbc.Row([
                        dbc.Col([
                                dbc.Card(dbc.CardBody([
                                    html.H3("Select your view:"),
                                    dbc.ButtonGroup([
                                        dbc.Button("Explore",id="exp"),
                                        dbc.Button("Compare",id="comp")]),
                                    html.Br(),
                                    html.P(id="test_output")])
                                ),
                                dbc.Card(dbc.CardBody([
                                    html.H1("Top Game is:"),
                                    html.P("COD"),
                                    html.P("# of sales and % of Global")
                                    ])
                                ),
                                dbc.Card(dbc.CardBody([
                                    html.H1("Top Region is:"),
                                    html.P("North America"),
                                    html.P("# of sales and % of Global")
                                    ])
                            ),     
                                dbc.Card(dbc.CardBody([
                                    html.H1("Top Genre is:"),
                                    html.P("Fighting"),
                                    html.P("# of sales and % of Global")
                                    ])
                            ),      
                                dbc.Card(dbc.CardBody([
                                    html.H1("Top Platform is:"),
                                    html.P("Wii"),
                                    html.P("# of sales and % of Global")
                                    ])
                            ),    
                                dbc.Card(dbc.CardBody([
                                    html.H1("Top Publisher is:"),
                                    html.P("Nintendo"),
                                    html.P("# of sales and % of Global")
                                    ]))
                        ],width=4),
                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Card(dbc.CardBody([
                                        html.Iframe(
                                            id = "time_sales",
                                            style={'border-width': '0', 'width': '1000px', 'height': '450px'}
                                        )
                                        ])),
                                    dbc.Card(dbc.CardBody([
                                        html.P("BELOW GRAPH?")
                                        ]))
                                ])
                            ])  
                        ],width=8)
                        ])
                    ],style={'margin-left': '0'})
                ])

@app.callback(
    Output("test_output", "children"),
    Output("exp", "active"),
    Output("comp", "active"),
    Input("exp", "n_clicks"),
    Input("comp", "n_clicks"))
def toggle_buttons(n_expl, n_comp):
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if ((n_expl is None) & (n_comp is None)):
        return f"Default to explore", True, False
    elif button_id == "exp":
        return f"Explore currently selected", True, False
    elif button_id == "comp":
        return f"Compare is selected", False, True














#Call back for table
@app.callback(
    Output("datatable","data"), #Output to ID: datatable for value:data
    Input("region_filter","value"),
    Input("table_display","value"))
def update_table(region_filter,n):
    filtered_data = sales_data[sales_data.Region==region_filter].sort_values("Sales",ascending=False)[0:n]
    return filtered_data.to_dict("records")

#Call back for Tab 1 - Graph 1: Region sales
@app.callback(
    Output("region_sales","srcDoc"), #Output to ID: titles_graph for value:srcDoc
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

#Call back for Tab 1 - Graph 2: Time sales
@app.callback(
    Output("time_sales","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def title_plot(region_filter,max_year=2020):
    sorted_genre = list(sales_data[sales_data.Region==region_filter].groupby("Genre").sum().sort_values("Sales",ascending=False).index)
    filtered_set = sales_data[sales_data.Year <= max_year].groupby(["Name","Genre","Region"]).sum().reset_index()[["Name","Genre","Region","Sales"]]
    chart = alt.Chart(
    sales_data[sales_data.Region==region_filter],
    title="Millions of copies sold per year").mark_bar().encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("sum(Sales):Q", title="Number of copies sold"),
    color=alt.Color('Genre:N', scale=alt.Scale(scheme='category20')),
    tooltip=["Genre:N","sum(Sales):Q"]
    )
    return chart.to_html()

#Call back for Tab 2 - Graph 1: Region releases
@app.callback(
    Output("region_releases","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def title_plot(region_filter,max_year=2020):
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

#Call back for Tab 2 - Graph 2: Time releases
@app.callback(
    Output("time_releases","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def title_plot(region_filter,max_year=2020):
    sorted_genre = list(sales_data[sales_data.Region==region_filter].groupby("Genre").sum().sort_values("Sales",ascending=False).index)
    filtered_set = sales_data[sales_data.Year <= max_year].groupby(["Name","Genre","Region"]).sum().reset_index()[["Name","Genre","Region","Sales"]]
    chart = alt.Chart(
    sales_data[sales_data.Region==region_filter],
    title="Number of releases per year").mark_bar().encode(
    x=alt.X("Year:O", title="Year"),
    y=alt.Y("count(Name):Q", title="Number of copies sold"),
    color=alt.Color('Genre:N', scale=alt.Scale(scheme='category20')),
    tooltip=["Genre:N","count(Name):Q"]
    )
    return chart.to_html()

#Call back for Tab 3 - Graph 1: Title performance
@app.callback(
    Output("title_perf_graph","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def title_plot(region_filter,max_year=2020):
    sorted_genre = list(sales_data[sales_data.Region==region_filter].groupby("Genre").sum().sort_values("Sales",ascending=False).index)
    filtered_set = sales_data[sales_data.Year <= max_year].groupby(["Name","Genre","Region"]).sum().reset_index()[["Name","Genre","Region","Sales"]]
    chart=alt.Chart(filtered_set[filtered_set.Region==region_filter]).mark_circle(size=50).encode(
        alt.X("Genre",sort=sorted_genre,title=None),
        alt.Y("Sales:Q",stack=None, title="Sales (in millions)"),
        alt.Color("Genre",scale=alt.Scale(scheme='category20'),legend=None),
        alt.Tooltip("Name"))
    chart = chart + alt.Chart(filtered_set[filtered_set.Region==region_filter].sort_values("Sales",ascending=False).iloc[:5,]).mark_text(align = "left", dx=10).encode(
        alt.X("Genre",sort=sorted_genre),
        alt.Y("Sales:Q"),
        text="Name").properties(title = "By Game Title")
    return chart.to_html()

#Call back for Tab 3 - Graph 2: Platform performance 
@app.callback(
    Output("platform_perf_graph","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def platform_plot(region_filter,max_year=2020):
    sorted_genre = list(sales_data[(sales_data.Region==region_filter) & (sales_data.Year <= max_year)].groupby("Genre").sum().sort_values("Sales",ascending=False).index)   
    filtered_set = sales_data_platform[sales_data_platform.Year <= max_year].groupby(["Platform","Genre","Region"]).sum().reset_index()[["Platform","Genre","Region","Sales"]]

    chart=alt.Chart(filtered_set[filtered_set.Region==region_filter]).mark_circle(size=50).encode(
        alt.X("Genre",sort=sorted_genre,title=None),
        alt.Y("Sales:Q",stack=None, title="Sales (in millions)"),
        alt.Color("Genre",scale=alt.Scale(scheme='category20'),legend=None),
        alt.Tooltip("Platform"))
    chart = chart + alt.Chart(filtered_set[filtered_set.Region==region_filter].sort_values("Sales",ascending=False).iloc[:5,]).mark_text(align = "left", dx=10).encode(
        alt.X("Genre",sort=sorted_genre),
        alt.Y("Sales:Q"),
        text="Platform").properties(title = "By Platform")
    return chart.to_html()

#Call back for Tab 3 - Graph 3: Publisher performance
@app.callback(
    Output("publisher_perf_graph","srcDoc"), #Output to ID: titles_graph for value:srcDoc
    Input("region_filter","value"))
def publisher_plot(region_filter,max_year=2020):
    sorted_genre = list(sales_data[(sales_data.Region==region_filter) & (sales_data.Year <= max_year)].groupby("Genre").sum().sort_values("Sales",ascending=False).index)   
    filtered_set = sales_data_publisher[sales_data_publisher.Year <= max_year].groupby(["Publisher","Genre","Region"]).sum().reset_index()[["Publisher","Genre","Region","Sales"]]

    chart=alt.Chart(filtered_set[filtered_set.Region==region_filter]).mark_circle(size=50).encode(
        alt.X("Genre",sort=sorted_genre,title=None),
        alt.Y("Sales:Q",stack=None, title="Sales (in millions)"),
        alt.Color("Genre",scale=alt.Scale(scheme='category20')),
        alt.Tooltip("Publisher"))
    chart = chart + alt.Chart(filtered_set[filtered_set.Region==region_filter].sort_values("Sales",ascending=False).iloc[:5,]).mark_text(align = "left", dx=10).encode(
        alt.X("Genre",sort=sorted_genre),
        alt.Y("Sales:Q"),
        text="Publisher").properties(title = "By Publisher")
    return chart.to_html()

#Convention
if __name__ == '__main__':
    app.run_server(debug=True, port = 8051)






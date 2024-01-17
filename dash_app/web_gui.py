import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

#Theme loaded: SLATE. Can change.
app = dash.Dash(__name__, use_pages=True, pages_folder="./", external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True)
load_figure_template('slate')

#Sidebar and main page implementations taken from DBC's documentation
sidebar_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
}
content_style = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
sidebar = html.Div(
    [
        html.H2("NY News Project", className="display-4"),
        html.Hr(),
        html.P(
            "The New York Times at a Glance", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Articles", href="/articles", active="exact"),
                #dbc.NavLink("Books", href="/books", active="exact"), Not implemented yet
                dbc.NavLink("Newswire", href="/newswire", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style = sidebar_style
)

#Overall page layout, do not modify
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    html.Div([dash.page_container],id = 'page-content', style=content_style)
])

#App title
app.title = 'NYT Newswire API Dashboard'

if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0")

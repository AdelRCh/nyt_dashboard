import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

#Landing page
layout = html.Div([
    html.H1('The New York Times as seen by three distinct APIs.'),
    html.Br(),
    dcc.Markdown("""The New York Times' wealth of information can be difficult to sift through, especially when the outlet publishes 100 articles per day on average. In this context, some news may fall through the cracks.

If that was not problematic enough, given the amount of nonfiction book releases, books of potential interest will fall through the cracks be it in the news cycle or due to daily life events.

Our project goes beyond covering those aspects as it makes an effort to look through news cycle related trends, using the Times' [publicly available IT resources.](https://developer.nytimes.com/)""",
link_target='_blank') #Opens a new tab if someone clicks on the NYT API Portal link.
])

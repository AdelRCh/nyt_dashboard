import os
import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pymongo
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dash.register_page(__name__)

#Receiving our data from MongoDB
MONGO_LABEL = os.environ.get('MONGODB_ADDRESS','localhost') #Unless you have your own address
MONGO_PORT = int(os.environ.get('MONGODB_PORT',27017)) #Unless you have a specific port, default is 27017
DB_CLIENT = pymongo.MongoClient(MONGO_LABEL, MONGO_PORT) # pymongo.MongoClient(host=MONGO_LABEL, port=MONGO_PORT)
db = DB_CLIENT['NY_Project']

articlesearch = db['ny_articles'] #Kenan's NY Articles Collection

#Article Search Section
pipeline = [
    {
        '$group': {
            '_id': '$news_desk',
            # 'section_word_count': {'$sum': '$word_count'},
            'section_word_count': {'$avg': '$word_count'},
            'section_article_count': {'$sum': 1},
            'newest_articles': {
                '$push': {
                    'headline': '$headline',
                    'web_url': '$web_url',
                    'pub_date': '$pub_date'
                }
            }
        }
    },
    {
        '$group': {
            '_id': None,
            'average_word_count': {'$avg': '$section_word_count'},
            'total_article_count': {'$sum': '$section_article_count'},
            'sections': {
                '$push': {
                    'section': '$_id',
                    'average_word_count': {'$avg': '$section_word_count'},
                    'article_count': '$section_article_count'
                }
            },
            'all_articles': {'$push': '$newest_articles'}
        }
    },
    {
        '$project': {
            'average_word_count': 1,
            'total_article_count': 1,
            'sections': 1,
            # Flatten the array of arrays
            'flattened_articles': {'$reduce': {
                'input': '$all_articles',
                'initialValue': [],
                'in': {'$concatArrays': ['$$value', '$$this']}
            }}
        }
    },
    {
        '$unwind': '$flattened_articles'
    },
    {
        '$sort': {'flattened_articles.pub_date': -1}
    },
    {
        '$limit': 5
    },
    {
        '$group': {
            '_id': '$_id',
            'average_word_count': {'$first': '$average_word_count'},
            'total_article_count': {'$first': '$total_article_count'},
            'sections': {'$first': '$sections'},
            'newest_articles': {'$push': '$flattened_articles'}
        }
    }
]

result_article_search = list(articlesearch.aggregate(pipeline))

if result_article_search:
   # Extracting data from the 'result' for 'sections'
    sections_data = [    {'section': section['section'], 'count': section['article_count']}
        for section in result_article_search[0]['sections']
    ]

    # # Save aggregated data into a new collection
    # aggregated_data_collection = db.ny_articles_aggregated_data
    # aggregated_data_collection.insert_one({
    #     'total_articles': sum(section['count'] for section in sections_data),
    #     'average_word_count': result[0]['average_word_count'],
    #     'sections': sections_data,
    #     'newest_articles': result[0]['newest_articles'],
    #     'timestamp': datetime.now()
    # })

    # # Extract total number of articles, average word count, sections with counts, and newest articles
    total_articles = result_article_search[0]["total_article_count"]
    average_word_count = result_article_search[0]["average_word_count"]
    sections = [section['section'] for section in result_article_search[0]['sections']]
    article_counts = [section['article_count'] for section in result_article_search[0]['sections']]
    newest_articles = result_article_search[0]['newest_articles']

    ## Figure
    # Extract the data for the scatter plot
    scatter_data = result_article_search[0]['sections']

#Article search: Plotly
# Create a scatter plot using Plotly Express
fig_article = px.scatter(
    scatter_data,
    x='article_count',
    y='average_word_count',
    text='section',
    labels={'article_count': 'Number of Articles', 'average_word_count': 'Average Word Count'},
    color='section',
    title='Number of Articles vs Average Word Count per Section',
    template='plotly_dark'
)
fig_article.update_layout(
        {
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )

# Scatter plot showing number of articles vs average word count per section
scatter_plot = dcc.Graph(
    id='section-scatter-plot',
    figure=fig_article,
    config={'displayModeBar': False}  # Hide the interactive mode bar
)

tab_art_landing = html.Div([
    html.H2(children='NY Times Article Statistics'),
    html.Div(children=f'Total articles: {total_articles}', style={'marginBottom': 20}),
    html.Div(children=f'The average word count is: {average_word_count:.2f}', style={'marginBottom': 20}),
    html.Br(),
    html.H2("5 Latest Articles:"),
    # Create a list of links to the 5 newest articles
    html.Ul([
        html.Li(html.A(article['headline']['main'], href=article['web_url'],target='_blank'), style={'list-style-type': 'none'}) for article in newest_articles
    ])]
    )

tab_art_graph = html.Div([
    html.H2("Scatter Plot: Number of Articles vs Average Word Count per Section"),
    scatter_plot
    ])

tab_art_sections_detailed = html.Div([
    html.H2("Articles per Section:"),
    html.Br(),
    # Create a list of sections and counts
    html.Ul([
        html.Li(f"{section}: {count} articles") for section, count in zip(sections, article_counts)
    ])
])

tab_art_search = html.Div(children=[

    # Search bar
    html.H2("Article Search"),
    dcc.Input(id='search-input', type='text', placeholder='Enter keywords...'),

    # Create a list of links to the articles based on the search results
    html.Ul(id='search-results')

])

article_tabs = dbc.Tabs([
    dbc.Tab([tab_art_landing, tab_art_search], label='Articles at a Glance'),
    dbc.Tab(tab_art_graph, label='Word Count Distribution Per Section'),
    dbc.Tab(tab_art_sections_detailed, label='More Section Info')
])

#On first load and on reload
article_tabs.active_tab = 'tab-0'

layout = html.Div([article_tabs])

# Define callback to update search results
@callback(
    Output('search-results', 'children'),
    [Input('search-input', 'value')],
    prevent_initial_call=True
)
def update_search_results(search_query):
    # MongoDB query to find articles containing the search query in keywords
    search_pipeline = [
        {'$match': {'keywords.value': {'$regex': f'{search_query}', '$options': 'i'}}},
        {'$project': {'headline': '$headline.main', 'web_url': '$web_url', '_id': 0}},
        {'$limit': 5}
    ]

    search_results = list(articlesearch.aggregate(search_pipeline))

    # Display search results as links
    result_links = [
        html.Li(html.A(result['headline'], href=result['web_url'],target='_blank')) for result in search_results
    ]

    return result_links

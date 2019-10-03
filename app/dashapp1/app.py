import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_d3cloud
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from app.dashapp1.data_container import DataContainer

obj_dc = DataContainer(f"{os.getcwd()}/app/dashapp1/assets/twitter_small.csv")

x_dates, y_freq = obj_dc.tweets_by_date()
date_ranges = obj_dc.dates_range

date_mark = {i: {'label' : date_ranges[i], 'style':{'color':'white'}} for i in range(0, len(date_ranges))}

trace_1 = go.Scatter(x=x_dates, y=y_freq, name='date', line=dict(width=2, color='rgb(229, 151, 50)'))

stock_layout = go.Layout(hovermode='closest',

                         xaxis={'title': 'Date'},
                         yaxis={'title': 'Tweets Frequency'}, margin={'t': 0})

fig = go.Figure(data=[trace_1], layout=stock_layout)

# df_map= obj_dc.tweets_by_geo()
df_map = pd.read_csv(f"{os.getcwd()}/app/dashapp1/assets/df_map.csv")

px.set_mapbox_access_token(
    'pk.eyJ1IjoiZ2lsdHJhcG8iLCJhIjoiY2o4eWJyNzY4MXQ1ZDJ3b2JsZHZxb3N0ciJ9.MROnmydnXtfjqjIBtC-P5g')
fig_map = px.scatter_mapbox(df_map, lat="lat", lon="long", text='location', color="number_of_tweets",
                            size="number_of_tweets",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=20, zoom=4.6, )
fig_map.update_layout(margin=dict(t=0))

fig_cord_freq = go.Figure(go.Bar(
    x=df_map['number_of_tweets'].tolist(),
    y=df_map['location'].tolist(),
    orientation='h'), layout=go.Layout(xaxis={'title': 'Frequency'},
                                       yaxis={'title': 'Geo Locations'}, height=600, margin=dict(t=0)))

hashtag_mostcommon = obj_dc.get_Top_hashtags(top_n=20)

df_hashtag_cord_freq = obj_dc.hashtag_freq_by_geo(most_common=hashtag_mostcommon)

fig_hashtag_cord_freq = go.Figure()

for idx in range(1, len(df_hashtag_cord_freq.columns)):
    fig_hashtag_cord_freq.add_trace(go.Bar(
        y=df_map['location'],
        x=df_hashtag_cord_freq.iloc[:, idx],
        name=df_hashtag_cord_freq.columns[idx],
        orientation='h'
    ))

fig_hashtag_cord_freq.update_layout(xaxis={'title': 'Frequency'},
                                    yaxis={'title': 'Geo Locations'}, barmode='stack', height=600, margin=dict(t=0))

ls_top_hashtags = [item[0] for item in hashtag_mostcommon]
ls_top_hashtags_freq = [item[1] for item in hashtag_mostcommon]

fig_hashtag_freq = go.Figure(go.Bar(
    x=ls_top_hashtags_freq,
    y=ls_top_hashtags,
    orientation='h'), layout=go.Layout(xaxis={'title': 'Frequency'},
                                       yaxis={'title': 'Top 20 Hashtags'}, height=600, margin=dict(t=0)))

hashtags_wordcloud = [{"text": a, "value": b} for a, b in obj_dc.get_Top_hashtags(top_n=200)]

mentions_wordcloud = [{"text": a, "value": b} for a, b in obj_dc.get_Top_mentions(top_n=200)]


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Img(src="https://dash-gallery.plotly.host/dash-oil-gas-ternary/assets/dash-logo.png"),
            html.H6("Twitter Tweets Analysis"),
        ],
    )


def build_graph_title(title):
    return html.P(className="graph-title", children=title)


def create_dash_app(name, flask_app_obj, url_base_path, assets_path,  meta_tags):

    global obj_dc, date_ranges, stock_layout

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
                                                    'https://gitcdn.link/repo/hassanbest/css_dumps/master/base.css',
                                                    'https://min.gitcdn.link/repo/hassanbest/css_dumps/master/base2.css',
                                                    ],
                    server=flask_app_obj,
                    url_base_pathname=url_base_path,
                    assets_folder=assets_path,
                    meta_tags=meta_tags)

    navbar = dbc.NavbarSimple(
        [
            dbc.Row(
                [
                    dbc.Col(

                        html.A(dbc.Button("Logout", color="primary", className="ml-2"), id='logout_dash', href="/logout",
                               style={'float': 'right'})
                    )]
            ),
        ],
        color="dark",
        dark=True,
        sticky="top"
    )

    main_layout =html.Div(
        children=[
            navbar,
            html.Div(
                id="top-row",
                children=[
                    html.Div(
                        className="row",
                        id="top-row-header",
                        children=[
                            html.Div(
                                id="header-container",
                                children=[
                                    build_banner(),
                                    html.P(
                                        id="instructions",
                                        children="Dashboard visualizations could be selected by "
                                                 "clicking on individual data points or using the lasso tool to capture "
                                                 "multiple data points or bars." ,
                                    ),
                                    build_graph_title("Filter by Year"),

                                    html.Div([

                                        # range slider
                                        html.P([
                                            dcc.RangeSlider(id='slider',
                                                            marks=date_mark,
                                                            min=0,
                                                            max=len(date_ranges) - 1,
                                                            value=[0, len(date_ranges) - 1])
                                        ])

                                    ])

                                ],
                            )
                        ],
                    ),
                    html.Div(
                        className="row",
                        id="top-row-graphs",
                        children=[
                            html.Div(
                                id="ternary-map-container",
                                children=[
                                    html.Div(
                                        id="ternary-header",
                                        children=[
                                            build_graph_title(
                                                "Tweets by Day/Month/Year"
                                            )
                                        ], style={'marginLeft': '100px', 'marginRight': '100px'}
                                    ),

                                    html.Div([
                                        dcc.Graph(id='plot', figure=fig),
                                    ], style={'marginLeft': '100px','marginRight': '100px', 'marginBottom': '50px'})

                                ],
                            ),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="row",
                id="bottom-row",
                children=[
                    
                    html.Div(
                        id="form-bar-container",
                        className="seven columns",
                        children=[
                            build_graph_title('Tweets Frequency by Location'),
                            dcc.Graph(id='plot_cord_freq', figure=fig_cord_freq),
                        ],
                    ),
                    html.Div(
                        
                        id="well-production-container",
                        className="five columns",
                        children=[
                            build_graph_title('Tweets Frequency Map'),
                            dcc.Graph(id='plot_map', figure=fig_map),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="row",
                id="bottom-row1",
                children=[
                    
                    html.Div(
                        id="form-bar-container1",
                        className="seven columns",
                        children=[
                            build_graph_title('Frequency of Top 20 Hashtags by Location'),
                            dcc.Graph(id='plot_hashtag_cord_freq', figure=fig_hashtag_cord_freq)],
                    ),
                    html.Div(
                        
                        id="well-production-container1",
                        className="five columns",
                        children=[
                            build_graph_title('Frequency of Top 20 Hashtags'),
                            dcc.Graph(id='plot_hashtag_freq', figure=fig_hashtag_freq)
                        ],
                    ),
                ],
            ),

            html.Div(
                className="row",
                id="bottom-row2",
                children=[
                    build_graph_title('Word Cloud - Top Hashtags'),
                    html.Div(
                        id="form-bar-container2",
                        className="twelve columns",
                        children=[
                            dash_d3cloud.WordCloud(
                                id='hashtags_cloud',
                                words=hashtags_wordcloud,
                                options={'spiral': 'rectangular',
                                         'scale': 'log',
                                         'rotations': 2,
                                         'rotationAngles': [0, -90]
                                         },
                            )
                        ], style={'backgroundColor': 'white'}
                    )
                ],
            ),

            html.Div(
                className="row",
                id="bottom-row3",
                children=[
                    build_graph_title('Word Cloud - Top Mentions'),
                    html.Div(
                        id="well-production-container2",
                        className="twelve columns",
                        children=[
                            dash_d3cloud.WordCloud(
                                id='mentions_cloud',
                                words=mentions_wordcloud,
                                options={'spiral': 'rectangular',
                                         'scale': 'log',
                                         'rotations': 2,
                                         'rotationAngles': [0, -90]
                                         },
                            )], style={'backgroundColor': 'white'}
                    )
                ],
            ),

        ]
    )

    app.layout = main_layout

    return app


def register_callbacks(dashapp):
    @dashapp.callback(Output('plot', 'figure'),
                      [Input('slider', 'value')])
    def update_figure(X):
        _x_dates, _y_freq = obj_dc.tweets_by_date(dt1=date_ranges[X[0]], dt2=date_ranges[X[1]])
        trace_1 = go.Scatter(x=_x_dates, y=_y_freq, name='date', line=dict(width=2, color='rgb(229, 151, 50)'))
        fig = go.Figure(data=[trace_1], layout=stock_layout)
        return fig


# if __name__ == "__main__":
#     app.run_server(debug=True)

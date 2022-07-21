import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import glob
import os
import re
from util import get_hash_for_img, get_best_match_idx
from util import img_directory, kps_directory, src_image_route, kps_image_route
import numpy as np
from flask_caching import Cache


def glob_re(pattern, strings):
    return list(filter(re.compile(pattern).match, strings))


dash.register_page(__name__, path="/", title="Frame Game Solver")

cache = Cache(
    dash.get_app().server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache",
        "CACHE_DEFAULT_TIMEOUT": 86400,
    },
)

list_of_images = glob_re("frame\d+-full.\w+", os.listdir(img_directory))

sort_order = lambda x: int(x.split("-")[0].split("frame")[1])

list_of_images = sorted(list_of_images, key=sort_order)

get_hash_for_img = cache.memoize()(get_hash_for_img)
hashes = [get_hash_for_img(path) for path in list_of_images]


layout = dbc.Container(
    [
        dbc.Row(
            html.A(
                html.H1("Frame Game Solver"),
                href="/",
                className="text-decoration-none text-reset",
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Form(
                            [
                                dbc.Row(
                                    [
                                        dbc.Label(
                                            "Game", html_for="frame-dropdown", width=2
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id="frame-dropdown",
                                                options=[
                                                    {"label": i, "value": i}
                                                    for i in range(
                                                        1, 1 + len(list_of_images)
                                                    )
                                                ],
                                                value=1,
                                                clearable=False,
                                            ),
                                            width=6,
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Label(
                                            "Hint #",
                                            html_for="frame-subslider",
                                            width=2,
                                        ),
                                        dbc.Col(
                                            dcc.Slider(
                                                id="frame-subslider",
                                                min=1,
                                                max=1,
                                                step=1,
                                                value=1,
                                            ),
                                            width=6,
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Switch(
                                                id="keypoint-toggle",
                                                label="Show Keypoints",
                                                value=False,
                                            ),
                                            width=6,
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                            ]
                        ),
                        dbc.Row(
                            dbc.Col(
                                [
                                    html.H4("Hint Image"),
                                    html.Img(id="test_image", style={"width": "100%"}),
                                ],
                                width=6,
                            ),
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.P(
                            [
                                "John Siracusa's ",
                                html.A(
                                    "Frame Game",
                                    href="https://hypercritical.co/frame-game",
                                ),
                                """
                                challenges participants to identify the film or TV
                                series from a small still image from the source. Hints are given by
                                progressively increasing the area of the still image.
                                """,
                            ]
                        ),
                        html.P(
                            [
                                "Siracusa started the Frame Game on his ",
                                html.A("twitter", href="https://twitter.com/siracusa"),
                                ". In a ",
                                html.A(
                                    "blog post",
                                    href="https://hypercritical.co/2022/04/25/frame-game",
                                ),
                                " he wrote: ",
                                "",
                            ]
                        ),
                        html.P(
                            [
                                html.I(
                                    "Have some people figured out how to use computers or web searches to brute-force this game? Almost certainly."
                                )
                            ]
                        ),
                        html.P(
                            [
                                "This site serves as a proof of concept to do exactly that. ",
                                html.A("Read how it works", href="/about"),
                                ".",
                            ]
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        dbc.Row(dbc.Col(html.Hr(), width=12)),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    dbc.Card(
                                        dbc.CardBody(
                                            html.Img(
                                                id="source_image", className="img-fluid"
                                            )
                                        )
                                    ),
                                    label="Matched Image",
                                ),
                                dbc.Tab(
                                    dbc.Card(
                                        dbc.CardBody(
                                            dcc.Graph(
                                                id="match-graph",
                                                config={"displayModeBar": False},
                                            ),
                                        )
                                    ),
                                    label="Data",
                                ),
                            ]
                        ),
                    ],
                    width=12,
                ),
            ]
        ),
    ],
    className="mb-5 mt-3",
)


@callback(
    Output("frame-subslider", "disabled"),
    Output("frame-subslider", "max"),
    Output("frame-subslider", "value"),
    Input("frame-dropdown", "value"),
)
def update_image_src(value):
    images = glob_re(f"frame{value}-\d+.\w+", os.listdir(img_directory))
    return False if len(images) > 1 else True, len(images), 1


@callback(
    Output("test_image", "src"),
    Output("source_image", "src"),
    Output("match-graph", "figure"),
    [
        Input("frame-dropdown", "value"),
        Input("frame-subslider", "value"),
        Input("keypoint-toggle", "value"),
    ],
)
def update_results(frame_no, hint_no, keypoint):

    # Get hashes from test img
    print(f"frame{frame_no}-{hint_no}.\w+", glob_re(f"frame{frame_no}-{hint_no}.\w+", os.listdir(img_directory)))
    test_path = glob_re(f"frame{frame_no}-{hint_no}.\w+", os.listdir(img_directory))[0]
    try:
        test_hashes = get_hash_for_img(test_path)

        hash_overlaps = []

        for i in range(len(list_of_images)):
            hash_overlaps.append(
                len(set.intersection(set(test_hashes), set(hashes[i])))
            )

        if np.max(hash_overlaps) == 0:
            raise Exception

        match_idx = np.argmax(hash_overlaps)
        best_frame_no = match_idx + 1
    except:
        test_hashes = None
        hash_overlaps = np.zeros(len(list_of_images))

    # Set the test img url
    if keypoint:
        path = glob_re(f"frame{frame_no}-{hint_no}-kps.\w+", os.listdir(kps_directory))[
            0
        ]
        test_image_path = f"{kps_image_route}{path}"
    else:
        path = glob_re(f"frame{frame_no}-{hint_no}.\w+", os.listdir(img_directory))[0]
        test_image_path = f"{src_image_route}{path}"

    # Set the source img url
    if test_hashes:
        if keypoint:
            path = path = glob_re(
                f"frame{best_frame_no}-full-kps.\w+", os.listdir(kps_directory)
            )[0]
            source_img_path = f"{kps_image_route}{path}"
        else:
            path = path = glob_re(
                f"frame{best_frame_no}-full.\w+", os.listdir(img_directory)
            )[0]
            source_img_path = f"{src_image_route}{path}"
    else:
        source_img_path = f"/static/sad_mac.jpg"

    # Set the figure data
    fig_data = go.Bar(
        x=np.arange(1, 1 + len(list_of_images)),
        y=hash_overlaps,
    )
    fig_layout = {"xaxis_title": "Image Number", "yaxis_title": "Number of Matches"}
    figure = go.Figure(data=[fig_data], layout=fig_layout)

    return test_image_path, source_img_path, figure

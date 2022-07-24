import os
import pickle

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from util import glob_re, kps_image_route, sort_images, src_image_route


def argmax(iter):
    max_val = None
    max_pos = 0
    for i in range(len(iter)):
        if max_val is None or iter[i] > max_val:
            max_val = iter[i]
            max_pos = i

    return max_pos


dash.register_page(__name__, path="/", title="Frame Game Solver")

list_of_images = sort_images(
    glob_re("frame\d+-full.\w+", os.listdir(f".{src_image_route}"))
)


with open("kp_data.pickle", "rb") as file:
    hash_dict = pickle.load(file)

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
                                            "Frame", html_for="frame-dropdown", width=2
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
                                            width=3,
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    "🔼",
                                                    id="frame-up-btn",
                                                    color="",
                                                    className="px-0",
                                                ),
                                                dbc.Button(
                                                    "🔽",
                                                    id="frame-dn-btn",
                                                    color="",
                                                    className="px-0",
                                                ),
                                            ],
                                            width=2,
                                            className="px-0",
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
                                    dcc.Loading(
                                        html.Img(
                                            id="test_image", style={"width": "100%"}
                                        )
                                    ),
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
                            ],
                            style={"border-left": "thin solid black"},
                            className="p-3",
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
                                            dcc.Loading(
                                                html.Img(
                                                    id="source_image",
                                                    className="img-fluid",
                                                )
                                            ),
                                            className="text-center",
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
    Output("frame-dropdown", "value"),
    Input("frame-dn-btn", "n_clicks"),
    Input("frame-up-btn", "n_clicks"),
    State("frame-dropdown", "value"),
)
def decrement_frame(n_clicks_dn, n_clicks_up, frame_val):
    changed_id = [p["prop_id"] for p in callback_context.triggered][0]
    if "frame-dn-btn" in changed_id:
        if frame_val <= 1:
            return 1
        return frame_val - 1
    elif "frame-up-btn" in changed_id:
        if frame_val >= len(list_of_images):
            return len(list_of_images)
        return frame_val + 1
    else:
        return 1


@callback(
    Output("frame-subslider", "disabled"),
    Output("frame-subslider", "max"),
    Output("frame-subslider", "value"),
    Input("frame-dropdown", "value"),
)
def update_image_src(value):
    images = glob_re(f"frame{value}-\d+.\w+", os.listdir(f".{src_image_route}"))
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
    changed_ids = [p["prop_id"] for p in callback_context.triggered]
    if changed_ids == ["."]:
        raise PreventUpdate

    # Get hashes from test img
    test_path = f"frame{frame_no}-{hint_no}.jpg"

    try:
        test_hashes = hash_dict[test_path]

        hash_overlaps = []

        for image_name in list_of_images:
            hash_overlaps.append(
                len(set.intersection(set(test_hashes), set(hash_dict[image_name])))
            )

        if max(hash_overlaps) == 0:
            raise Exception

        match_idx = argmax(hash_overlaps)
        best_frame_no = match_idx + 1
    except:
        test_hashes = None
        hash_overlaps = [0 for i in range(len(list_of_images))]

    test_image_path = f"{kps_image_route if keypoint else src_image_route}frame{frame_no}-{hint_no}{'-kps' if keypoint else ''}.jpg"

    if test_hashes:
        source_image_path = f"{kps_image_route if keypoint else src_image_route}frame{frame_no}-full{'-kps' if keypoint else ''}.jpg"
    else:
        source_image_path = f"/assets/sad_mac.jpg"

    # Set the figure data
    fig_data = go.Bar(
        x=[i for i in range(1, 1 + len(list_of_images))],
        y=hash_overlaps,
    )
    fig_layout = {"xaxis_title": "Image Number", "yaxis_title": "Number of Matches"}
    figure = go.Figure(data=[fig_data], layout=fig_layout)

    return test_image_path, source_image_path, figure

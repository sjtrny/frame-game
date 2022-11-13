import os
import pickle
from urllib.parse import urlencode

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, callback, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from app_util import apply_default_value, dash_kwarg, parse_state
from util import glob_re, kps_image_route, sort_images, src_image_route

#
# def argmax(iter):
#     max_val = None
#     max_pos = 0
#     for i in range(len(iter)):
#         if max_val is None or iter[i] > max_val:
#             max_val = iter[i]
#             max_pos = i
#
#     return max_pos


dash.register_page(__name__, path="/", title="Frame Game Solver")

list_of_images = sort_images(
    glob_re("frame\d+-full.\w+", os.listdir(f".{src_image_route}"))
)


with open("kp_data.pickle", "rb") as file:
    hash_dict = pickle.load(file)


def build_layout(params):
    return [
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            apply_default_value(params)(dbc.Switch)(
                                id="keypoints",
                                label="Show Keypoints",
                                value=False,
                            ),
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label(
                            "Frame",
                        ),
                        apply_default_value(params)(dcc.Dropdown)(
                            id="frame",
                            options=[
                                {"label": i, "value": i}
                                for i in range(
                                    1,
                                    1 + len(list_of_images),
                                )
                            ],
                            value=1,
                            clearable=False,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    [
                        dbc.Label(
                            "Hint",
                            html_for="hint-num",
                        ),
                        apply_default_value(params)(dcc.Slider)(
                            id="hint-num",
                            min=1,
                            max=1,
                            step=1,
                            value=1,
                            included=False,
                        ),
                    ],
                    className="mb-2",
                ),
                dbc.Row(
                    dbc.Col(
                        [
                            dcc.Loading(
                                html.A(
                                    children=[
                                        html.Img(
                                            id="test_image",
                                            className="img-fluid",
                                        )
                                    ],
                                    id="test_image_link",
                                )
                            ),
                        ],
                    ),
                ),
            ],
        ),
    ]


layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(html.A("About", href="/about", className="nav-link")),
            ],
            brand="Frame Game Solver",
            brand_href="/",
            color="dark",
            dark=True,
            className="mb-4",
        ),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H4("Controls"),
                                html.Div(id="page-layout", children=build_layout([])),
                            ],
                            lg=3, xs=12, className='mb-3'
                        ),
                        dbc.Col(
                            [
                                html.H4("Best Frame Match"),
                                dcc.Loading(
                                    html.A(
                                        children=[
                                            html.Img(
                                                id="source_image",
                                                className="img-fluid",
                                            )
                                        ],
                                        id="source_image_link",
                                    )
                                ),
                            ],
                            lg=7, xs=12, className='mb-3'
                        ),
                        dbc.Col(
                            [html.H4("Frame Matches"), html.Div(id="match-list")],
                            lg=2, xs=12, className='mb-3'
                        ),
                    ]
                ),
            ],
            className="mb-5 mt-3",
        ),
    ]
)

components = [
    ("frame", "value"),
]

graph_inputs = [Input(x[0], x[1]) for x in components]


@callback(
    Output("page-layout", "children"),
    inputs=[Input("url", "href")],
)
def page_load(href):
    if not href:
        return []
    state = parse_state(href)
    return build_layout(state)


@callback(
    Output("url", "search"),
    inputs=graph_inputs,
)
# Add dash kward arg here
@dash_kwarg(graph_inputs)
def update_url_state(**kwargs):
    state = urlencode(kwargs)
    return f"?{state}"


@callback(
    Output("hint-num", "disabled"),
    Output("hint-num", "max"),
    Output("hint-num", "value"),
    Input("frame", "value"),
)
def update_image_src(value):
    images = glob_re(f"frame{value}-\d+.\w+", os.listdir(f".{src_image_route}"))
    return False if len(images) > 1 else True, len(images), 1


@callback(
    Output("test_image", "src"),
    Output("test_image_link", "href"),
    Output("source_image", "src"),
    Output("source_image_link", "href"),
    Output("match-list", "children"),
    [
        Input("frame", "value"),
        Input("hint-num", "value"),
        Input("keypoints", "value"),
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

        # match_idx = argmax(hash_overlaps)
        sorted_idx = np.argsort(hash_overlaps)
        match_idx = sorted_idx[-1]
        best_frame_no = match_idx + 1

    except:
        test_hashes = None
        hash_overlaps = [0 for i in range(len(list_of_images))]

    test_image_path = f"{kps_image_route if keypoint else src_image_route}frame{frame_no}-{hint_no}{'-kps' if keypoint else ''}.jpg"

    if test_hashes:
        source_image_path = f"{kps_image_route if keypoint else src_image_route}frame{frame_no}-full{'-kps' if keypoint else ''}.jpg"
        match_list_children = [
            html.Ol(
                [
                    html.Li(f"Frame {idx+1} - {hash_overlaps[idx]} hits")
                    for idx in sorted_idx[::-1][:10]
                    if hash_overlaps[idx] > 0
                ]
            )
        ]
    else:
        source_image_path = f"/assets/sad_mac.jpg"
        match_list_children = ["No matches"]

    return (
        test_image_path,
        test_image_path,
        source_image_path,
        source_image_path,
        match_list_children,
    )

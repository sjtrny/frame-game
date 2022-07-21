from dash import Dash, dcc, html, Input, Output
import dash
import dash_bootstrap_components as dbc
import flask
from util import src_image_route, kps_image_route
from util import img_directory, kps_directory

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

app.layout = dash.page_container

# Serve images
@app.server.route(f"/{src_image_route}/<image_path>")
def serve_src_image(image_path):
    return flask.send_from_directory(img_directory, image_path)


# Serve images
@app.server.route(f"/{kps_image_route}/<image_path>")
def serve_kps_image(image_path):
    return flask.send_from_directory(kps_directory, image_path)


if __name__ == "__main__":
    app.run_server(debug=True)

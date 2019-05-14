from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for, jsonify, session, g, \
    make_response, send_file
from werkzeug.contrib.fixers import ProxyFix
import pandas as pd
import utils
import bjoern
import click
from flask_cors.extension import CORS
import sqltap.wsgi
import cache
from cache import cache_region
import git_repo
from engine import widgets
import matplotlib
import mpld3
from ipywidgets.embed import embed_data
from ipywidgets import IntSlider
import json

UPLOAD_FOLDER = '/tmp'

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key'
))

app.wsgi_app = ProxyFix(app.wsgi_app)

def get_figures():
    figs = [manager.canvas.figure for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]

    matplotlib._pylab_helpers.Gcf.destroy_all()

    return figs


@app.route('/', endpoint='index', methods=['GET', 'POST'])
def index():
    interact = widgets.expected_damage('Darthur')
    sliders = interact.widget.children
    data = embed_data(sliders)

    figs = get_figures()

    manager_state = json.dumps(data['manager_state'])
    widget_views = [json.dumps(view) for view in data['view_specs']]

    return render_template('index.html', sha=git_repo.sha, matplot=mpld3.fig_to_html(figs[0]),
                           manager_state=manager_state, widget_views=widget_views)

@app.route('/test', endpoint='test', methods=['GET'])
def test():
    s1 = IntSlider(max=200, value=100)
    s2 = IntSlider(value=40)
    data = embed_data(views=[s1, s2])

    html_template = """
    <html>
      <head>

        <title>Widget export</title>

        <!-- Load RequireJS, used by the IPywidgets for dependency management -->
        <script 
          src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js" 
          integrity="sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=" 
          crossorigin="anonymous">
        </script>

        <!-- Load IPywidgets bundle for embedding. -->
        <script
          data-jupyter-widgets-cdn="https://cdn.jsdelivr.net/npm/"
          src="https://unpkg.com/@jupyter-widgets/html-manager@*/dist/embed-amd.js" 
          crossorigin="anonymous">
        </script>

        <!-- The state of all the widget models on the page -->
        <script type="application/vnd.jupyter.widget-state+json">
          {manager_state}
        </script>
      </head>

      <body>

        <h1>Widget export</h1>

        <div id="first-slider-widget">
          <!-- This script tag will be replaced by the view's DOM tree -->
          <script type="application/vnd.jupyter.widget-view+json">
            {widget_views[0]}
          </script>
        </div>

        <hrule />

        <div id="second-slider-widget">
          <!-- This script tag will be replaced by the view's DOM tree -->
          <script type="application/vnd.jupyter.widget-view+json">
            {widget_views[1]}
          </script>
        </div>

      </body>
    </html>
    """

    manager_state = json.dumps(data['manager_state'])
    widget_views = [json.dumps(view) for view in data['view_specs']]
    rendered_template = html_template.format(manager_state=manager_state, widget_views=widget_views)

    return rendered_template

@app.route('/test2', endpoint='test2', methods=['GET'])
def test2():
    interact = widgets.expected_damage('Darthur')
    sliders = interact.widget.children
    data = embed_data(sliders)

    html_template = """
    <html>
      <head>

        <title>Widget export</title>

        <!-- Load RequireJS, used by the IPywidgets for dependency management -->
        <script 
          src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js" 
          integrity="sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=" 
          crossorigin="anonymous">
        </script>

        <!-- Load IPywidgets bundle for embedding. -->
        <script
          data-jupyter-widgets-cdn="https://cdn.jsdelivr.net/npm/"
          src="https://unpkg.com/@jupyter-widgets/html-manager@*/dist/embed-amd.js" 
          crossorigin="anonymous">
        </script>

        <!-- The state of all the widget models on the page -->
        <script type="application/vnd.jupyter.widget-state+json">
          {manager_state}
        </script>
      </head>

      <body>

        <h1>Widget export</h1>

        <div id="first-slider-widget">
          <!-- This script tag will be replaced by the view's DOM tree -->
          <script type="application/vnd.jupyter.widget-view+json">
            {widget_views[0]}
          </script>
        </div>

        <hrule />

        <div id="second-slider-widget">
          <!-- This script tag will be replaced by the view's DOM tree -->
          <script type="application/vnd.jupyter.widget-view+json">
            {widget_views[1]}
          </script>
        </div>

      </body>
    </html>
    """

    manager_state = json.dumps(data['manager_state'])
    widget_views = [json.dumps(view) for view in data['view_specs']]
    rendered_template = html_template.format(manager_state=manager_state, widget_views=widget_views)

    return rendered_template

CORS(app)

app.wsgi_app = sqltap.wsgi.SQLTapMiddleware(app.wsgi_app)

@click.command()
@click.option('-d', '--debug', is_flag=True)
@click.option('-p', '--port', type=click.INT, default=8000)
@click.option('-h', '--host', default='0.0.0.0')
def main(debug, port, host):
    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        bjoern.run(app.wsgi_app, host=host, port=port)

if __name__ == '__main__':
    main()


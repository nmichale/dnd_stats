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
from ipywidgets.embed import embed_minimal_html

UPLOAD_FOLDER = '/tmp'

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='development key'
))

app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/', endpoint='index', methods = ['GET', 'POST'])
def index():

    return render_template('index.html', sha=git_repo.sha)

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


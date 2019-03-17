import bjoern
import click
import connexion
import flask
from flask_cors.extension import CORS
import utils
import sqltap.wsgi
import config

app = connexion.FlaskApp(__name__)
app.app.config['JSON_SORT_KEYS'] = False

ui_bp = flask.Blueprint('ui', __name__)

@ui_bp.route('/swagger_ui')
@ui_bp.route('/swagger_ui/')
def serve_swagger_ui_index():
    return flask.render_template('swagger_ui.html', api_url=flask.request.url_root + 'swagger_ui.json')


@ui_bp.route('/swagger_ui/<path:filename>')
def serve_swagger_ui_static_files(filename):
    return flask.send_from_directory('static', filename)

@ui_bp.route('/swagger_ui.json')
def serve_swagger_ui_json():
    return utils.yaml_to_json(config.wd + '/' + config.SPEC_FN)

app.app.register_blueprint(ui_bp)

app.add_api('api.yaml')

CORS(app.app)

app.app.wsgi_app = sqltap.wsgi.SQLTapMiddleware(app.app.wsgi_app)

@click.command()
@click.option('-d', '--debug', is_flag=True)
@click.option('-p', '--port', type=click.INT, default=8000)
@click.option('-h', '--host', default='0.0.0.0')
def main(debug, port, host):
    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        bjoern.run(app.app.wsgi_app, host=host, port=port)

if __name__ == '__main__':
    main()

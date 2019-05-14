import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import matplotlib
matplotlib.use('Agg')

# Monkey patch the show command to disable, since this pauses the thread.
import matplotlib.pyplot
import matplotlib.pyplot.mpld3
matplotlib.pyplot.show = matplotlib.pytplit.pld3.show

from api_app import app as api
from ui import app as gui
from werkzeug.wsgi import DispatcherMiddleware
import click
import bjoern
import config
import flask

application = DispatcherMiddleware(api.app.wsgi_app, {config.gui_path: gui.wsgi_app})

@click.command()
@click.option('-d', '--debug', is_flag=True)
@click.option('-p', '--port', type=click.INT, default=8000)
@click.option('-h', '--host', default='0.0.0.0')
def main(debug, port, host):
    if debug:
        app = flask.Flask(__name__)
        app.wsgi_app = application
        app.run(host=host, port=port, debug=True)
    else:
        bjoern.run(application, host=host, port=port)

if __name__ == '__main__':
    main()
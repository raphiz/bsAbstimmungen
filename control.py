from bsAbstimmungen import manage
from bsAbstimmungen import utils
from bsAbstimmungen import setup_logging
import argh
from datetime import datetime
import http.server
import socketserver


@argh.arg('from_date', help='The first date to importing data from '
          '(eg. 24.03.2015)')
@argh.arg('to_date', help='The last date to import data from (eg. 24.03.2015)')
def import_data(from_date, to_date):
    from_date = datetime.strptime(from_date, '%d.%m.%Y')
    to_date = datetime.strptime(to_date, '%d.%m.%Y')
    manage.import_data(from_date, to_date)


def render():
    manage.render()


def serve():
    with utils.pushd('build/site'):
        server_address = ('', 8080)
        httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
        httpd.serve_forever()

parser = argh.ArghParser()
parser.add_commands([import_data, render, serve])


if __name__ == '__main__':
    setup_logging()
    parser.dispatch()

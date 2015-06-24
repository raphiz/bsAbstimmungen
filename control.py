from bsAbstimmungen import manage
from bsAbstimmungen import setup_logging
import argh
from datetime import datetime


@argh.arg('from_date', help='The first date to importing data from '
          '(eg. 24.03.2015)')
@argh.arg('to_date', help='The last date to import data from (eg. 24.03.2015)')
def import_data(from_date, to_date):
    from_date = datetime.strptime(from_date, '%d.%m.%Y')
    to_date = datetime.strptime(to_date, '%d.%m.%Y')
    manage.import_data(from_date, to_date)

parser = argh.ArghParser()
parser.add_commands([import_data])


if __name__ == '__main__':
    setup_logging()
    parser.dispatch()

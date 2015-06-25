from jinja2 import Environment, FileSystemLoader
from ..models import *
import os
import shutil
import logging
import re

logger = logging.getLogger(__name__)


template_dir = 'templates/'
destination_dir = 'build/site/'


def render():
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['toUrl'] = toUrl

    # Copy resources
    shutil.copytree(template_dir + 'assets', destination_dir + 'assets')

    councillors = Councillor.select()
    for councillor in councillors:
        name = 'grossraete/{0}/index'.format(toUrl(councillor.fullname))
        render_page(env, 'councillor_details', name, councillor=councillor, title=councillor.fullname)
    render_page(env, 'councillor_index', 'grossraete/index', councillors=councillors, title='Grossräte')

    render_page(env, 'compare', 'vergleichen/index')


def toUrl(value):
    replacements = {' ': '_', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
                    'à': 'a', 'ë': 'e', 'é': 'e'}
    for k, v in replacements.items():
        value = value.replace(k, v)
    if not re.fullmatch('[a-zA-Z_]*', value):
        logger.warn('Found unsupported URL car in: ' + value)
    return value.lower()


def render_page(env, src, dst, **kwargs):
    directory = destination_dir + os.path.dirname(dst)
    if not os.path.exists(directory):
        os.makedirs(directory)

    file = os.path.basename(dst)
    template = env.get_template("{0}.html".format(src))
    template.stream(**kwargs).dump('{0}/{1}.html'.format(directory, file))
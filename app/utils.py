from __future__ import print_function
import pandas as pd
import urllib
import sys
import yaml
import collections
import json
from flask import make_response, send_file
from werkzeug.utils import secure_filename
import connexion
import datetime
import flask

def df_html(df, index=False, font_size=None):
    with pd.option_context('display.max_colwidth', -1):
        df_style = (
            df.style.format(lambda x: '{:,.12g}'.format(x) if isinstance(x, float) else x)
        )

        if not index:
            df_style = df_style.hide_index()

        if font_size is not None:
            df_style = df_style.set_properties(**{'font-size': font_size})

        html = df_style.render()
        return html

def ajax_form_to_dict(s):
    return dict([e.split('=') for e in s.split('&')])

def decode_dict(d):
    return {str(k): (str(v) if isinstance(v, unicode) else v) for k,v in d.items()}

def unescape_dict(d):
    d = {str(urllib.unquote_plus(key)): (str(urllib.unquote_plus(value)) if isinstance(value, unicode) else value)
         for key, value in d.items()}
    return d

def strip_spaces(df):
    return df.applymap(lambda x: x.rstrip() if isinstance(x, (str, unicode)) else x)

def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def quotes_or_null(val):
    if val == '' or pd.isnull(val):
        return 'NULL'
    else:
        return "'"+val+"'"

def timedelta_to_string(td):
    seconds = td.seconds
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '{} days {} hours {} minutes'.format(td.days, h, m)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_row_unique(key, df, keyname=None):
    if isinstance(df, list):
        df = pd.Series(df)

    if isinstance(df, pd.DataFrame):
        row = df[df[keyname] == key]
    else:
        row = df[df == key]

    L = row.shape[0]
    if L == 0:
        raise KeyError('Could not find "{}" with value: "{}".'.format(keyname, key))
    elif L > 1:
        raise KeyError('Duplicated "{}" with value: "{}".'.format(keyname, key))
    else:
        return row.iloc[0]

def yaml_to_json(fn):
    # Setup support for ordered dicts so we do not lose ordering
    # when importing from YAML
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

    def dict_representer(dumper, data):
        return dumper.represent_mapping(_mapping_tag, data.iteritems())

    def dict_constructor(loader, node):
        return collections.OrderedDict(loader.construct_pairs(node))

    yaml.add_representer(collections.OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor)

    data = yaml.load(open(fn))
    return json.dumps(data, indent=2)


def serve_content(df):
    content_type = connexion.request.headers['accept']

    if content_type == 'text/csv':
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        path = connexion.request.path
        r = flask.make_response(df.to_csv(index=False))
        filename = secure_filename("{}_{}.csv".format(path,ts))
        r.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
        r.headers["Content-Type"] = content_type
        return r
    else:
        return df.to_dict(orient='records')

def get_required_fields(definition):
    markup = yaml.load(open(config.wd + '/' + config.SPEC_FN))
    required = markup['definitions'][definition]['required']
    return required

def check_required_fields(definition, data):
    required = get_required_fields(definition)

    for r in required:
        if r not in data.keys():
            raise KeyError("Required field "
                           "'{}' not included in post body.".format(r))

def fill_missing_fields(definition, data, number_fill=0, string_fill=None, bool_fill=False, array_fill=[],
                        object_fill={}):

    with open(config.wd + '/' + config.SPEC_FN) as f:
        definitions = yaml.load(f)['definitions']

    for param, val in definitions[definition]['properties'].items():
        if isinstance(val, dict) and '$ref' in val and 'definitions' in val['$ref']:
            val = definitions[val['$ref'].split('/')[2]]

        if not isinstance(val, dict) or 'type' not in val.keys():
            continue

        if param not in data.keys():
            type = val['type']
            if type == 'number':
                data[param] = number_fill
            elif type == 'string':
                data[param] = string_fill
            elif type == 'boolean':
                data[param] = bool_fill
            elif type == 'array':
                data[param] = array_fill
            elif type == 'object':
                data[param] = object_fill

    return data

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return float('.'.join([i, (d+'0'*n)[:n]]))

def create_pdf_response(path):
    response = send_file(path)
    return response

def create_csv_response(path):
    df = pd.read_csv(path, low_memory=False)
    html = df_html(df)
    response = make_response(html)
    return response

def create_excel_response(path):
    with open(path, 'rb') as f:
        df = pd.read_excel(f)
        html = df_html(df)
        response = make_response(html)
        return response

def create_docx_response(path):
    '''
    Add mammoth==1.4.5 to requirements.txt if you need this.

    :param path:
    :return:
    '''
    with open(path, 'rb') as doc:
        html = mammoth.convert_to_html(doc).value.encode('utf8')
        response = make_response(html)
        return response

def create_html_response(path):
    return send_file(path)

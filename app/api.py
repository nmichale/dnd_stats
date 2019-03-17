import utils
import json
import yaml
import traceback
import pandas as pd
import cache
from cache import cache_region

SUCCESS_CODE = 200
ERROR_CODE = 400

def example(parameter=None):
    df = pd.DataFrame({'success': [True], 'message': ['Example']})
    content = utils.serve_content(df)
    return content, SUCCESS_CODE
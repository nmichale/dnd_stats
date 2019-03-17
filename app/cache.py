import dogpile.cache
from dogpile.cache.region import make_region
import os
import uuid
from flask import session

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

cache_region = make_region().configure(
    'dogpile.cache.redis',
    arguments = {
        'host': REDIS_HOST,
        'port': 6379,
        'redis_expiration_time': 60*60*2,
        'distributed_lock': True
    }
)

append_id_list = lambda l, id : [e + '_' + id for e in l]
append_id_dict = lambda d, id: dict(zip(append_id_list(d.keys(), id), d.values()))
instance_vars = ['example']
gen_instance_keys = lambda id: append_id_list(instance_vars, id)

def set_instance_cache(d):
    id = get_session_id()
    d = append_id_dict(d, id)
    cache_region.set_multi(d)

def get_cache_dict(k):
    v = cache_region.get_multi(k)
    return dict(zip(k,v))

def clear_instance_cache():
    id = get_session_id()
    instance_keys = gen_instance_keys(id)
    instance_dict = dict(zip(instance_keys, [None for e in instance_keys]))
    cache_region.set_multi(instance_dict)

def get_set_instance_cache():
    id = get_session_id()
    instance_keys = gen_instance_keys(id)
    cache_dict = get_cache_dict(instance_keys)

    for k,v in cache_dict.items():
        if isinstance(v, dogpile.cache.api.NoValue):
            cache_region.set(k, None)
            cache_dict[k] = cache_region.get(k)

    cache_dict = {(k.replace('_'+id,'')):v for k,v in cache_dict.items()}

    return cache_dict

def get_session_id():
    if 'id' in session:
        return session['id'].bytes
    else:
        session_id = uuid.uuid4()
        session['id'] = session_id
        return session_id.bytes
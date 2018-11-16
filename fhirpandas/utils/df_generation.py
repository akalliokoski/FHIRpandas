import pandas as pd

import fhirpandas.constants.meta as meta
import fhirpandas.constants.resources.encounter as ce

def _getvalue(obj, path, default = None):
    if (len(path) == 0 or obj == None):
        return default
    
    next_attr = path.pop(0)

    next_obj = None
    if (isinstance(obj, list)):
        next_obj = _getlistvalue(obj, next_attr, default)
    else:
        next_obj = getattr(obj, next_attr, default)

    if (len(path) == 0):
        return next_obj
    
    return _getvalue(next_obj, path, default)

def _getlistvalue(lst, index, default = None):
    return lst[index] if index < len(lst) else default

def _createdict(resource):
    res_type = resource.resource_type
    paths = meta.paths(res_type)
    columns = meta.columns(res_type)
    values = [_getvalue(resource, paths[c].copy()) for c in columns]
    return dict(zip(columns, values))

def create_df(resources):
    # TODO: use ids as index
    # TODO: set data types
    dicts = [_createdict(e) for e in resources]
    return pd.DataFrame(dicts)
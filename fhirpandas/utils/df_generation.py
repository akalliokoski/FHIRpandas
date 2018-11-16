import pandas as pd

import fhirpandas.constants.meta as meta
import fhirpandas.constants.resources.encounter as ce

def _getValue(obj, path, default = None):
    if (len(path) == 0 or obj == None):
        return default
    
    nextAttr = path.pop(0)

    nextObj = None
    if (isinstance(obj, list)):
        nextObj = _getListValue(obj, nextAttr, default)
    else:
        nextObj = getattr(obj, nextAttr, default)

    if (len(path) == 0):
        return nextObj
    
    return _getValue(nextObj, path, default)

def _getListValue(lst, index, default = None):
    return lst[index] if index < len(lst) else default

def _resourceToDict(resource):
    res_type = resource.resource_type
    paths = meta.paths(res_type)
    columns = meta.columns(res_type)
    values = [_getValue(resource, paths[c].copy()) for c in columns]
    return dict(zip(columns, values))

def create_df(resources):
    # TODO: use ids as index
    # TODO: set data types
    encounterDicts = [_resourceToDict(e) for e in resources]
    return pd.DataFrame(encounterDicts)
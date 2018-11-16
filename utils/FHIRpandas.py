
from pathlib import Path
from functools import reduce
import json
import fhirclient.models.bundle as b
import fhirclient.models.patient as p
from fhirclient.models.fhirabstractbase import FHIRValidationError
import pandas as pd

import utils.constants.meta as meta
import utils.constants.encounters as ec

# TODO: memory optimization, performance optimization
#   ? flag for disabling bundles and resource cache?
#   ? flush method

def fromJSON(path, strict=False):
    # TODO: how to handle relative path?
    #    * check from pandas.from_csv
    json_path = Path(path)
    if (not json_path.is_dir()):
        # TODO: throw expections (path )?
        # how does pandas handle it from.csv
        return None
    
    results = {p.stem:_load_bundle(p, strict) for p in json_path.glob('*.json')}
    bundles = {key:item[0] for key, item in results.items() if item[0] != None}
    validation_errors = {key:item[1] for key, item in results.items() if item[1] != None}

    return FHIRpandas(bundles, validation_errors)

def _load_bundle(path, strict):
    error = None

    try:
        with open(path) as file:
            json_data = json.load(file)
            bundle = b.Bundle(json_data)
    except FHIRValidationError as validation_error:
        bundle = None
        error = validation_error
        if (strict):
            raise validation_error
    except:
        print(f'Unexpected error: {sys.exc_info()[0]}')
        raise

    return (bundle, error)

class FHIRpandas:

    _encounters = None

    def __init__(self, bundles, validation_errors):
        self.bundles = bundles
        self.validation_errors = validation_errors

    def _getResourcesFromBundle(self, bundle, resource_type):
        if (bundle.entry == None):
            return []
        
        return [entry.resource for entry in bundle.entry if entry.resource.resource_type == resource_type]

    def _appendResources(self, acc, bundle, resourceType):
        acc.extend(self._getResourcesFromBundle(bundle, resourceType))
        return acc

    def _getResources(self, resourceType):
        resources = reduce(
            lambda acc, bundle: self._appendResources(acc, bundle, resourceType),
            self.bundles.values(),
            [])
        
        ids = [r.id for r in resources]
        missing_ids = any([r.id == None for r in resources])
        if (missing_ids):
            ids = None
            
        return (resources, ids)

    def _getEncounters(self):
        if (self._encounters == None):
            encounters, ids = self._getResources(ec.RESOURCE_TYPE)
            self._encounters = dict(zip(ids, encounters))

        return self._encounters

    def _getValue(self, obj, path, default = None):
        if (len(path) == 0 or obj == None):
            return default
        
        nextAttr = path.pop(0)

        nextObj = None
        if (isinstance(obj, list)):
            nextObj = self._getListValue(obj, nextAttr, default)
        else:
            nextObj = getattr(obj, nextAttr, default)

        if (len(path) == 0):
            return nextObj
        
        return self._getValue(nextObj, path, default)

    def _getListValue(self, lst, index, default = None):
        return lst[index] if index < len(lst) else default

    def _resourceToDict(self, resource):
        res_type = resource.resource_type
        paths = meta.paths(res_type)
        columns = meta.columns(res_type)
        values = [self._getValue(resource, paths[c].copy()) for c in columns]
        return dict(zip(columns, values))

    def encountersDataFrame(self):
        # TODO: use ids as index
        encounterDicts = [self._resourceToDict(e) for e in self._getEncounters().values()]
        return pd.DataFrame(encounterDicts)




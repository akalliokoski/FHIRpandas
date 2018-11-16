
from pathlib import Path
from functools import reduce
import json
import fhirclient.models.bundle as b
import fhirclient.models.patient as p
from fhirclient.models.fhirabstractbase import FHIRValidationError
import pandas as pd

import fhirpandas.constants.meta as meta
import fhirpandas.constants.resources.encounter as ce
import fhirpandas.utils.df_generation as df_generation

ENCOUNTER_RESOURCE_TYPE = ce.RESOURCE_TYPE

def from_json(path, strict=False):
    json_path = Path(path)
    if (not json_path.is_dir()):
        # TODO: throw expections (path )?
        # how does pandas handle it from.csv
        return None
    
    results = {p.stem:_load_bundle(p, strict) for p in json_path.glob('*.json')}
    bundles = {key:item[0] for key, item in results.items() if item[0] != None}
    validation_errors = {key:item[1] for key, item in results.items() if item[1] != None}

    return FhirPandas(bundles, validation_errors)

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

class FhirPandas:

    _resource_cache = {}

    def __init__(self, bundles, validation_errors):
        self.bundles = bundles
        self.validation_errors = validation_errors

    def _find_resources_from_bundle(self, bundle, resource_type):
        if (bundle.entry == None):
            return []
        
        return [entry.resource for entry in bundle.entry if entry.resource.resource_type == resource_type]

    def _append_resources(self, acc, bundle, resource_type):
        acc.extend(self._find_resources_from_bundle(bundle, resource_type))
        return acc

    def _find_resources(self, resource_type):
        resources = reduce(
            lambda acc, bundle: self._append_resources(acc, bundle, resource_type),
            self.bundles.values(),
            [])
        
        ids = [r.id for r in resources]
        missing_ids = any([r.id == None for r in resources])
        if (missing_ids):
            ids = None
            
        return (resources, ids)

    def _get_resources(self, resource_type):
        cached_res = self._resource_cache.get(resource_type, None)
        if (cached_res != None):
            return cached_res
        
        (resources, ids) = self._find_resources(resource_type)
        self._resource_cache[resource_type] = dict(zip(ids, resources))
        return resources

    def create_df(self, resource_type):
        resources = self._get_resources(resource_type)
        return df_generation.create_df(resources)

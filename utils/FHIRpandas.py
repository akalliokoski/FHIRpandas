
from pathlib import Path
from functools import reduce
import json
import fhirclient.models.bundle as b
import fhirclient.models.patient as p
from fhirclient.models.fhirabstractbase import FHIRValidationError
import pandas as pd

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
    invalidBundles = {key:item[1] for key, item in results.items() if item[1] != None}

    return FHIRpandas(bundles, invalidBundles)

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

    __ENCOUNTER_RESOURCE_TYPE__ = "Encounter"

    _encounters = None

    def __init__(self, bundles, invalidBundles):
        self.bundles = bundles
        self.invalidBundles = invalidBundles

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
            encounters, ids = self._getResources(self.__ENCOUNTER_RESOURCE_TYPE__)
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
    
    def _encounterToDict(self, encounter):
        # NOTE: SNOMED-CT code system expected
        #   Should used code system be added also?
        # NOTE: Only first of the codes (code, reason code) used
        return {
            "ID": encounter.id,
            "Start": self._getValue(encounter, ["period", "start", "date"]),
            "Stop": self._getValue(encounter, ["period", "end", "date"]),
            "Patient": self._getValue(encounter, ["subject", "reference"]),
            "EncounterClass": self._getValue(encounter, ["class_fhir", "code"]),
            "Code": self._getValue(encounter, ["type", 0, "coding", 0, "code"]),
            "Description": self._getValue(encounter, ["type", 0, "coding", 0, "display"]),
            "ReasonCode": self._getValue(encounter, ["reason", 0, "coding", 0, "code"]),
            "ReasonDescription": self._getValue(encounter, ["reason", 0, "coding", 0, "display"])
        }

    def encountersDataFrame(self):
        # TODO: use ids as index
        encounterDicts = [self._encounterToDict(e) for e in self._getEncounters().values()]
        return pd.DataFrame(encounterDicts)




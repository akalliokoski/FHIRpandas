
import utils.constants.resources.encounter as e

RESOURCE_TYPE = "RESOURCE_TYPE"
COLUMNS = "COLUMNS"
PATHS = "PATHS"

META = {
    e.RESOURCE_TYPE: {
        RESOURCE_TYPE: e.RESOURCE_TYPE,
        
        COLUMNS: [
            e.ID,
            e.START,
            e.STOP,
            e.PATIENT,
            e.ENCOUNTER_CLASS,
            e.CODE,
            e.DESCRIPTION,
            e.REASON_CODE,
            e.REASON_DESCRIPTION
        ],

        PATHS: {
            e.ID: ["id"],
            e.START: ["period", "start", "date"],
            e.STOP: ["period", "end", "date"],
            e.PATIENT: ["subject", "reference"],
            e.ENCOUNTER_CLASS: ["class_fhir", "code"],
            e.CODE: ["type", 0, "coding", 0, "code"],
            e.DESCRIPTION: ["type", 0, "coding", 0, "display"],
            e.REASON_CODE: ["reason", 0, "coding", 0, "code"],
            e.REASON_DESCRIPTION: ["reason", 0, "coding", 0, "display"]
        }
    }
}

def columns(resource_type):
    return META[resource_type][COLUMNS]

def paths(resource_type):
    return META[resource_type][PATHS]
    
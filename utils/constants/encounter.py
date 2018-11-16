
RESOURCE_TYPE = "Encounter"

ID = "ID"
START = "Start"
STOP = "Start"
PATIENT = "Patient"
ENCOUNTER_CLASS = "EncounterClass"
CODE = "Code"
DESCRIPTION = "Description"
REASON_CODE = "ReasonCode"
REASON_DESCRIPTION = "ReasonDescription"

COLUMNS = [
    ID,
    START,
    STOP,
    PATIENT,
    ENCOUNTER_CLASS,
    CODE,
    DESCRIPTION,
    REASON_CODE,
    REASON_DESCRIPTION
]

PATHS = {
    ID: ["id"],
    START: ["period", "start", "date"],
    STOP: ["period", "end", "date"],
    PATIENT: ["subject", "reference"],
    ENCOUNTER_CLASS: ["class_fhir", "code"],
    CODE: ["type", 0, "coding", 0, "code"],
    DESCRIPTION: ["type", 0, "coding", 0, "display"],
    REASON_CODE: ["reason", 0, "coding", 0, "code"],
    REASON_DESCRIPTION: ["reason", 0, "coding", 0, "display"]
}
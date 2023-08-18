import logging
import jsonschema

OBJ_JSON_SCHEMA = {
    "type": "object",
    "patternProperties": {
        ".*": {"type": "string"}
    }
}


def validate_keys(instance):
    for key in instance.keys():
        if key.strip() == "":
            raise jsonschema.exceptions.ValidationError("Keys must be non-empty strings")


def validate_json(data, schema=None):
    log.debug(f"validate_json")
    if schema is None:
        schema = OBJ_JSON_SCHEMA
    try:
        validate_keys(data)
        jsonschema.validate(instance=data, schema=schema)
        log.debug(f"VALID: {data}")
    except jsonschema.exceptions.ValidationError as e:
        log.error(f"ERROR: {data} - invalid")
        log.error(e)

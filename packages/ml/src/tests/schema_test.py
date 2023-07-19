import logging

import jsonschema

from utils.schema_validators import validate_json

data = {
    "entity1": "description of entity1. Describe the entities using sentences rather than single words.",
    "entity2": "description of entity2. Describe the entities using sentences rather than single words.",
    "entity3": "description of entity3. Describe the entities using sentences rather than single words.",
}

data1 = {
    "entity1": "description of entity1. Describe the entities using sentences rather than single words.",
    "entity2": "description of entity2. Describe the entities using sentences rather than single words.",
    "entity3": "description of entity3. Describe the entities using sentences rather than single words.",
    "h":1
}

data2 = {
    "jh": " ",
}
data3 = {
    "": " ",
}

validate_json(data)
validate_json(data1)
validate_json(data2)
validate_json(data3)
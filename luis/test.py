import jsonschema
import json

with open("user4.json") as file:
    obj = json.loads(file.read())

with open("UserSchema.schema.json") as file:
    schema = json.load(file)

try:
    jsonschema.validate(instance=obj, schema=schema)
    print("Validated")
except Exception:
    print("Error validating object")
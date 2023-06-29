import user
import json

def serialize_user(user):
    with open(f"{user.name}.json", "w") as file:
        text = json.dumps(user.__dict__, indent=2)
        file.write(text)

def deserialize_user(name):
    with open(f"{name}.json") as file:
        try:
            text = file.read()
            text = json.loads(text)
            dev = str(text)
            return user.user(text['name'], text['age'], text['previous_years'])
        except ValueError:
            print("No file has been found")
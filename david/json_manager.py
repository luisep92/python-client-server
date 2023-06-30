import user
import json

def serialize_user(user: user.User) -> None:
    with open(f"{user.name}.json", "w") as file:
        text = json.dumps(user.__dict__, indent=2)
        file.write(text)

def deserialize_user(name: str) -> user.User:
    with open(f"{name}.json") as file:
        try:
            text = file.read()
            text = json.loads(text)
            return user.User(text['name'], text['age'], text['previous_years'])
        except ValueError:
            print("No file has been found")
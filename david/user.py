from typing import List

class user:
    def __init__(self, name: str, age: int, previous_years: List[int]):
        self.name = name
        self.age = age
        self.previous_years = previous_years
        self.is_major = self.age >= 18
        print(f"Module_name: {repr(__name__)}")
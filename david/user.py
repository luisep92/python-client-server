from typing import List

class User:
    def __init__(self, name: str, age: int, previous_years: List[int]):
        self.name = name
        self.age = age
        self.previous_years = previous_years
        self.is_major = self.age >= 18
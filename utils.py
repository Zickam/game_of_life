class Vector2:
    def __init__(self, x: int | float, y: int | float):
        self.x = x
        self.y = y

    def getTuple(self):
        return self.x, self.y

    def __str__(self):
        return f"({self.x},{self.y}):{super().__str__()}"

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector2(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vector2(x, y)

    def __mul__(self, other):
        x = self.x * other.x
        y = self.y * other.y
        return Vector2(x, y)


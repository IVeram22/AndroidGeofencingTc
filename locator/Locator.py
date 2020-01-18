class Locator:

    def __init__(self, by, value, description, dynamic_value=None):
        self._by = by
        self._value = value
        self._description = description
        self.dynamic_value = dynamic_value

    def value(self):
        return self._value if self.dynamic_value is None else self._value % self.dynamic_value

    def by(self):
        return self._by

    def description(self):
        return self._description


def create_locator(by, value, description, dynamic_value=None):
    return Locator(
        by,
        value,
        description,
        dynamic_value
    )
class Token:
    def __init__(self, name):
        self.name = name
        self.attributes = {}

    def info(self):
        print(f"Name: {self.name}")
        print(f"Attribs: {self.attributes}")
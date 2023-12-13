class byte:
        def __init__(self, value):
            self.hexString = value
            self.hexValue = int(self.hexString, 16)
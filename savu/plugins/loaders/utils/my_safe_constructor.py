from yaml.constructor import SafeConstructor


# Create custom safe constructor class that inherits from SafeConstructor
class MySafeConstructor(SafeConstructor):

    # Create new method to handle boolean logic
    def add_bool(self, node):
        return self.construct_scalar(node)



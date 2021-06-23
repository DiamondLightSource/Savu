from yaml.constructor import SafeConstructor

# Create custom safe constructor class that inherits from SafeConstructor
class MySafeConstructor(SafeConstructor):

    # Create new method handle boolean logic
    def add_bool(self, node):
        return self.construct_scalar(node)

# Inject the above boolean logic into the custom constuctor
MySafeConstructor.add_constructor('tag:yaml.org,2002:bool',
                                      MySafeConstructor.add_bool)

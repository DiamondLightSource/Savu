from yaml.reader import *
from yaml.scanner import *
from yaml.parser import *
from yaml.composer import *
from yaml.resolver import *

from savu.plugins.loaders.utils.my_safe_constructor import MySafeConstructor


class MySafeLoader(
    Reader, Scanner, Parser, Composer, MySafeConstructor, Resolver
):
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        MySafeConstructor.__init__(self)
        Resolver.__init__(self)

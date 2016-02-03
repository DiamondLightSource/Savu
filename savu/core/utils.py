# Copyright 2015 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: utils
   :platform: Unix
   :synopsis: Simple core util methods
.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""

import logging


def logfunction(func):
    """decorator to add logging information around calls for use with ."""
    def _wrapper(*args, **kwds):
        logging.info("Start::%s:%s",
                     func.__module__,
                     func.__name__)
        returnval = func(*args, **kwds)
        logging.info("Finish::%s:%s",
                     func.__module__,
                     func.__name__)
        return returnval
    return _wrapper


def logmethod(func):
    """decorator to add logging information around calls for use with ."""
    def _wrapper(self, *args, **kwds):
        logging.info("Start::%s.%s:%s",
                     func.__module__,
                     self.__class__.__name__,
                     func.__name__)
        returnval = func(self, *args, **kwds)
        logging.info("Finish::%s.%s:%s",
                     func.__module__,
                     self.__class__.__name__,
                     func.__name__)
        return returnval
    return _wrapper


def import_class(class_name):
    name = class_name
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    temp = name.split('.')[-1]
    module2class = ''.join(x.capitalize() for x in temp.split('_'))
    return getattr(mod, module2class.split('.')[-1])


def add_base(clazz, ExtraBase):
    cls = clazz.__class__
    clazz.__class__ = cls.__class__(cls.__name__, (cls, ExtraBase), {})


@logfunction
def test():
    print("test")

USER_LOG_LEVEL = 100
USER_LOG_HANDLER = None

def user_message(message):
    logging.log(USER_LOG_LEVEL, message)
    if USER_LOG_HANDLER is not None:
        USER_LOG_HANDLER.flush()

def add_user_log_level():
    logging.addLevelName(USER_LOG_LEVEL, "USER")

def add_user_log_handler(logger, user_log_path):
    fh = logging.FileHandler(user_log_path, mode='w')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    fh.setLevel(USER_LOG_LEVEL)
    logger.addHandler(fh)
    USER_LOG_HANDLER = fh
    user_message("User Log Started")

# we register any existing plugins
# then we load the UI from the pyblish config manager
# now we can edit the registered plugins their settings in the UI, and save out a config

# this config can then be loaded in to apply the settings. see sample_apply_config.py

# TODO add option to create/edit config through CLI


from pyblish import api
from pyblish_config_creator import config_creator_GUI
import types
import sys

class Plugin1(api.ContextPlugin):
    order = api.CollectorOrder
    test1 = 1
    test2 = 2
    test3 = 3
    test4 = 4
    test5 = 5
    test6 = 6
    test7 = 7
    test8 = 8
    test9 = 9
    test10 = 10

class Plugin2(api.ContextPlugin):
    order = api.CollectorOrder

# api.deregister_all_paths()  # deregister default plugins for sample
api.register_plugin(Plugin1)
api.register_plugin(Plugin2)
api.register_host('maya')

# all this mocking is needed because pyblish_magenta plugins cant be imported outside maya due to cmds
# also a hack to load plugins depending on magenta since i don't have it correctly setup in my env
mock_module = types.ModuleType('mock')
mock_module.cmds = None
mock_module.mel = None
mock_module.api = None
modules_to_mock = ['maya', 'pyblish_magenta', 'maya.cmds', 'pyblish_magenta.api', 'pyblish_magenta.plugin',
                   'pyblish_magenta.utils', 'pyblish_magenta.vendor']
for name in modules_to_mock:
    sys.modules[name] = mock_module


config_creator_GUI.make_config()
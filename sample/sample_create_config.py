from pyblish import api
from pyblish_config import apply_config



class Plugin1(api.ContextPlugin):
    order = api.CollectorOrder

class Plugin2(api.ContextPlugin):
    order = api.CollectorOrder

#api.deregister_all_paths()  # deregister default plugins for sample
api.register_plugin(Plugin1)
api.register_plugin(Plugin2)

import pyblish_config.config_creator


# all this mocking is needed because pyblish_magenta plugins cant be imported outside maya due to cmds
# also a hack to load plugins depending on magenta since i don't have it correctly setup in my env
import types
import sys
mock_module = types.ModuleType('mock')
mock_module.cmds = None
mock_module.mel = None
mock_module.api = None
modules_to_mock = ['maya', 'pyblish_magenta', 'maya.cmds', 'pyblish_magenta.api', 'pyblish_magenta.plugin',
                   'pyblish_magenta.utils', 'pyblish_magenta.vendor']
for name in modules_to_mock:
    sys.modules[name] = mock_module

api.register_plugin_path(r'C:\Projects\tonictools-ta\3rd_party_packages\pyblish_maya\plugins\plugins') # i tossed the magenta plugins in here i know it's messy

pyblish_config.config_creator.make_config()



# api.register_plugin_path('C:/shared plugins')
# apply_config('sample_config.json')
#
# #print plugin settings before config applied
# for p in api.registered_plugins():
#     print(p.__name__, p.optional)
#
# plugins = api.discover()  # discover applies our filter and returns the new plugins
#
# for p in plugins:
#     print(p.__name__, p.optional)

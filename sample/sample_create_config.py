# we register any existing plugins
# then we load the UI from the pyblish config manager
# now we can edit the registered plugins their settings in the UI, and save out a config

# this config can then be loaded in to apply the settings. see sample_apply_config.py

# TODO add option to create/edit config through CLI


from pyblish import api
import pyblish_config.config_creator
import types
import sys


class Plugin1(api.ContextPlugin):
    order = api.CollectorOrder

class Plugin2(api.ContextPlugin):
    order = api.CollectorOrder

#api.deregister_all_paths()  # deregister default plugins for sample
api.register_plugin(Plugin1)
api.register_plugin(Plugin2)


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

api.register_plugin_path(r'C:\Projects\tonictools-ta\3rd_party_packages\pyblish_maya\plugins\plugins')  # i tossed the magenta plugins in here i know it's messy

pyblish_config.config_creator.make_config()
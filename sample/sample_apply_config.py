# register plugins
# apply config to overwrite which plugins are loaded
# and overwrite plugin settings


from pyblish import api
from pyblish_config.config import register_config_filter


# -------- create plugins --------
class Plugin1(api.ContextPlugin):
    order = api.CollectorOrder


class Plugin2(api.ContextPlugin):
    order = api.CollectorOrder


# -------- register plugins --------
api.deregister_all_paths()  # deregister default plugins for sample
api.register_plugin(Plugin1)
api.register_plugin(Plugin2)

# -------- debug print --------
# print plugin settings before config applied
for p in api.registered_plugins():
    print(p.__name__, p.optional)

# -------- register pipeline settings, ready to apply --------
register_config_filter('config_sample.json')

# -------- discover / applies config settings --------
# discover applies our filter and returns the new plugins
# discover finds plugins from registered folder paths, directly registered plugins, then applies filter
plugins = api.discover()
# we do not include discover in register config because the pyblish GUI runs discover

# -------- debug print --------
for p in plugins:
    print(p.__name__, p.optional)

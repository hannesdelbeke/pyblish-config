from pyblish import api
from pyblish_config import apply_config


class Plugin1(api.ContextPlugin):
    order = api.CollectorOrder

class Plugin2(api.ContextPlugin):
    order = api.CollectorOrder

api.deregister_all_paths()  # deregister default plugins for sample
api.register_plugin(Plugin1)
api.register_plugin(Plugin2)

api.register_plugin_path('C:/shared plugins')
apply_config('sample_config.json')

#print plugin settings before config applied
for p in api.registered_plugins():
    print(p.__name__, p.optional)

plugins = api.discover()  # discover applies our filter and returns the new plugins

for p in plugins:
    print(p.__name__, p.optional)

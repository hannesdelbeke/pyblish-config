from pyblish import api
import json


# does register_config imply we can have multiple filters?
def apply_config(config_path=None, config_dict=None):

    # default_settins (ex all enabled/disabled ....)
    # any plugins not in pipeline, should they be included or exluded


    def apply_config_filter(plugins):
        # we expect either the config path or the config data
        if config_path:
            f = open(config_path, )
            config_dict = json.load(f)
        elif not config_dict:
            raise Exception

        # # get settings per plugin
        # for plugin_name, plugin_config in data.items():
        # # todo raise error when an expected plugin is not found

        # get settings per plugin
        for plugin in plugins[:]:
            plugin_config = config_dict.get(plugin.__name__, {})  # plugins with same name might clash

            for key, value in plugin_config.items():
                # TODO  differentiate between input classes (action,plugin...)
                #  and raw input int,str...

                # aply settings to plugins
                setattr(plugin, key, value)


    api.register_discovery_filter(apply_config_filter)



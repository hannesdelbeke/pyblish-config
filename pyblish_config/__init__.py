from pyblish import api
import json


# does register_config imply we can have multiple filters?
# let's name it register because the filter only applies after discover has run.
# we need to support discover since the pyblish GUI uses it
def register_config_filter(config_path=None, config_dict=None):
    """
    register a plugin settings filter from a settings file,
    which overwrites the default plugin settings,
    and is applied when running pyblish discover

    :param config_path: path to config dict to load plugin settings from (json file)
    :param config_dict: pass a dict directly
    :return: None
    """

    # default_settins (ex all enabled/disabled ....)
    # any plugins not in pipeline, should they be included or exluded

    def config_filter_callback(plugins):
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

    api.register_discovery_filter(config_filter_callback)


# def apply_config(config_path=None, config_dict=None):
#     register_config_filter(config_path=config_path)
#     plugins = api.discover()
#     return plugins


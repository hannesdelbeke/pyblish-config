from pyblish import api
import json


# does register_config imply we can have multiple filters?
# let's name it register because the filter only applies after discover has run.
# we need to support discover since the pyblish GUI uses it
skip_attr = []#'repair', 'id', 'log', 'process', 'version', 'requires']
default_attributes = ['actions', 'active', 'families', 'order', 'plugin', 'hosts', 'label', 'match', 'optional',
                      'targets', 'version', 'requires', 'log', 'id', 'repair']


# plugin config: the config/settings of a single plugin

# pipeline config: the config/settings of all plugins in your pipeline, a dict of dicts of plugin configs
# since we use names you cant have 2 plugins  with the same name

# when it just says config this likely is pipeline config


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
            f = open(config_path)
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


def save_config(path, config_data):
    """save a config to a json. can be used on both pipeline and plugin configs"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4)

def load_config(config_path):
    """load a config from a json. can be used on both pipeline and plugin configs"""
    f = open(config_path)
    config_dict = json.load(f)
    return config_dict

def diff_pipeline_configs(config_new, config_original):
    # get differences between config and plugin settings
    # todo fix that
    #  naively assume differences can be calc between configs
    #  this wont work if we edit an already different config

    # this diff is only needed when doing register_plugin -> discover -> plugins ->config
    # when we edit an alrdy existing config we dont need to do any diffing

    config_data = {}
    for k, v in config_new.items():
        # if config2[k] != v:
        config_data[k] = {}

        for k2, v2 in v.items():
            if config_original[k][k2] != v2:
                config_data[k][k2] = v2

        # config_data[k] = v

    # set(self.pipeline_config)
    # set(self.pipeline_config.items())
    # difference = set(self.pipeline_config.items()) ^ set(self.original_pipeline_config.items())
    # config_data = dict(difference)

    return config_data


def get_pipeline_config_from_plugins(plugins):
    """
    from a list of plugins, get all plugin configs.
    save these in a single dict, the pipeline config
    """

    # store all plugin configs in the pipeline config
    pipeline_config = {}
    for plugin in plugins:
        pipeline_config[plugin.__name__] = get_plugin_config(plugin)

    return pipeline_config


def get_plugin_config(plugin):
    """
    get all attributes from the plugin class, and save them in a dict
    :param plugin: Pyblish plugin to get settings from
    :return: a dict containing plugin settings
    """
    # for every plugin, store all settings in the plugin config
    plugin_config = {}
    for attr in dir(plugin):
        if not attr.startswith('_'):  # and attr not in skip_attr and attr not in default_attributes:
            value = getattr(plugin, attr)
            plugin_config[attr] = value
    plugin_config['__doc__'] = plugin.__doc__
    return plugin_config
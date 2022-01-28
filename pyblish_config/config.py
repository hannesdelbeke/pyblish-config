from pyblish import api
import json


# does register_config imply we can have multiple filters?
# let's name it register because the filter only applies after discover has run.

# options
# - multiple pipeline filters. apply settings to plugins in order (could error on clash)
# - multiple pipeline filters, but only 1 active pipeline filter, able to switch pipeline
# - single pipeline only

# we need to support discover since the pyblish GUI uses it
# skip_attr = []#'repair', 'id', 'log', 'process', 'version', 'requires']


# plugin config: the config/settings of a single plugin

# pipeline config: the config/settings of all plugins in your pipeline, a dict of dicts of plugin configs
# since we use names you cant have 2 plugins  with the same name

# when it just says config this likely is pipeline config


def register_pipeline_config_filter(config_path=None, config_dict=None):
    """
    register a plugin settings filter from a settings file,
    which overwrites the default plugin settings,
    and is applied when running pyblish discover

    :param config_path: path to config dict to load plugin settings from (json file)
    :param config_dict: pass a dict directly
    :return: None
    """

    # we expect either the config path or the config data
    assert config_path or config_dict, "register_config_filter requires either a config path or a config dict, not both"

    if config_path:
        f = open(config_path)
        config_dict = json.load(f)
    elif not config_dict:
        raise Exception

    # default_settings (ex all enabled/disabled ....)
    # any plugins not in pipeline, should they be included or exluded

    def config_filter_callback(plugins):

        # raise error when an expected plugin is not found
        plugin_names = [p.data['name'] for p in plugins]
        for plugin_name in config_dict:
            if plugin_name not in plugin_names:
                raise Exception("plugin not found in pipeline: " + plugin_name)

        # get settings per plugin
        for plugin in plugins[:]:
            plugin_config = config_dict.get(plugin.__name__, {})  # plugins with same name might clash

            for key, value in plugin_config.items():
                # TODO  differentiate between input classes (action, plugin...) and raw input int,str...
                # custom load if value starts with #action| or #plugin|. ex: #action|modulename.action_name

                # aply settings to plugins
                setattr(plugin, key, value)

    api.register_discovery_filter(config_filter_callback)


# def apply_config(config_path=None, config_dict=None):
#     register_config_filter(config_path=config_path)
#     plugins = api.discover()
#     return plugins


def save_config_as_json(path, config_data):
    """save a config to a json. can be used on both pipeline and plugin configs"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4)


def load_config_from_json(config_path):
    """load a config from a json. can be used on both pipeline and plugin configs"""
    f = open(config_path)
    config_dict = json.load(f)
    return config_dict


def diff_pipeline_configs(config_new, config_original):
    """get differences between config and plugin settings"""
    config_data = {}
    for k, v in config_new.items():
        config_data[k] = {}
        for k2, v2 in v.items():
            if config_original[k][k2] != v2:
                config_data[k][k2] = v2
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
        if not attr.startswith('_') and attr not in ('id', 'log'):  # skip private, skip id & log, you should never change these
            value = getattr(plugin, attr)
            if hasattr(value, '__call__'):  # skip functions
                continue
            plugin_config[attr] = value
    # plugin_config['__doc__'] = plugin.__doc__
    return plugin_config
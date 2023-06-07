from pyblish import api
import pyblish.plugin
import json
import io
import logging


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


class PipelineConfig(dict):
    # TODO doesnt yet support methods like deepcopy, returns dict instead of Config.

    def filter_default_attributes(config):  # filter_default_attrs
        """ filter out default pyblish plugin attributes. example: families, id, ... """
        default_attrs = [x for x in iter_default_plugin_attrs()]
        for plugin_name, plugin_config in config.items():
            for attr_name in list(plugin_config.keys()):
                if attr_name in default_attrs:
                    plugin_config.pop(attr_name)

    def filter_attributes(config, attributes):  # filter_attrs
        """ filter out custom attributes. """
        for plugin_name, plugin_config in config.items():
            for attr_name in list(plugin_config.keys()):
                if attr_name in attributes:
                    plugin_config.pop(attr_name)

    def filter_private_attributes(config):
        """ filter out custom attributes. """
        for plugin_name, plugin_config in config.items():
            for attr_name in list(plugin_config.keys()):
                if attr_name.startswith('_'):
                    plugin_config.pop(attr_name)

    def filter_empty_plugins(config):  # filter_empty_plugins
        for plugin_name in list(config.keys()):
            plugin_config = config[plugin_name]
            if not plugin_config:
                config.pop(plugin_name)

    def dump(config, path):  # save_config_as_json
        """save a config to a json. can be used on both pipeline and plugin configs"""
        with io.open(path, 'w', encoding='utf-8') as outfile:
            try:
                # python 2
                my_json_str = json.dumps(config, ensure_ascii=False, indent=4)
                if isinstance(my_json_str, str):
                    my_json_str = my_json_str.decode("utf-8")
                outfile.write(my_json_str)

            except:
                # python 3
                json.dump(config, outfile, indent=4)

    def register(config):

        def config_filter_callback(plugins):

            # raise error when an expected plugin is not found
            plugin_names = [plugin.__name__ for plugin in plugins]
            for plugin_name in config:
                if plugin_name not in plugin_names:
                    raise Exception("plugin not found in pipeline: " + plugin_name)

            # get settings per plugin
            for plugin in plugins[:]:

                logging.debug("applying config to plugin: " + plugin.__name__)
                plugin_config = config.get(plugin.__name__, None)  # plugins with same name might clash

                # skip Pyblish plugins not in the config, this might be unwanted in same cases
                if plugin_config is None:
                    logging.debug("disabling plugin not in config: " + plugin.__name__)
                    plugin.active = False
                    continue

                for attr_name, value in plugin_config.items():
                    # TODO  differentiate between input classes (action, plugin...) and raw input int,str...
                    # custom load if value starts with #action| or #plugin|. ex: #action|modulename.action_name

                    # apply settings to plugins
                    setattr(plugin, attr_name, value)

        api.register_discovery_filter(config_filter_callback)


def iter_default_plugin_attrs(private=False):
    """ filter default pyblish attributes """
    variables = vars(pyblish.plugin.Plugin)
    for x in variables:
        if not private and x.startswith('_'):
            continue
        yield(x)


def iter_non_default_plugin_attrs(plugin):
    """ get non default pyblish attributes """
    default_attrs = list(iter_default_plugin_attrs())
    for x in vars(plugin):
        if x.startswith('_'):
            continue
        if x in default_attrs:
            continue
        yield(x)


# TODO remove this convenience function
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

    PipelineConfig(config_dict).register()


# def apply_config(config_path=None, config_dict=None):
#     register_config_filter(config_path=config_path)
#     plugins = api.discover()
#     return plugins


def load_config_from_json(config_path):
    """load a config from a json. can be used on both pipeline and plugin configs"""
    f = open(config_path)
    config_dict = json.load(f)
    return PipelineConfig(config_dict)


def diff_pipeline_configs(config_new, config_original):
    """get differences between config and plugin settings"""
    config_data = {}
    for k, v in config_new.items():
        config_data[k] = {}
        for k2, v2 in v.items():
            original_value = config_original[k][k2]
            if original_value != v2:

                if not original_value and not v2:  # example empty string and None
                    continue

                config_data[k][k2] = v2
    return PipelineConfig(config_data)


def get_pipeline_config_from_plugins(plugins):
    """
    from a list of plugins, get all plugin configs.
    save these in a single dict, the pipeline config
    """

    # store all plugin configs in the pipeline config
    pipeline_config = {}
    for plugin in plugins:
        pipeline_config[plugin.__name__] = get_plugin_config(plugin)

    return PipelineConfig(pipeline_config)


def type_is_supported(value):
    if hasattr(value, '__call__'):  # skip functions
        return
    if isinstance(value, type):  # skip classes
        return

    if isinstance(value, (list, tuple)) and len(value) > 0:
        value2 = value[0]
        return type_is_supported(value2)

    return True


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

            if not type_is_supported(value):
                continue

            plugin_config[attr] = value
    plugin_config['__doc__'] = plugin.__doc__
    return plugin_config
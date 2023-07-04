# pyblish-config [![PyPI](https://img.shields.io/pypi/v/pyblish-config)](https://pypi.org/project/pyblish-config/) 

## overwriting attributes
to make sure your pipeline doesnt break when updating plugins.
pyblish config only overwrites settings it finds in the settings file
it leaves everything else at default value.

example:
a plugin has various attributes. the json only contains a single attribute, node_type = "mesh"
all attributes of the plugin will remain the same except for the node_type.

### create a config file
see [sample_create_config](sample/sample_create_config.py)

### apply a config file
see [sample_apply_config](sample/sample_apply_config.py)

## explicitly registering plugins
the exception to this is the plugins registered.
it will only use plugins matching the plugin names in the settings file

example:
you have 5 plugins registered. the settings file has 3 plugins listed.
only those 3 plugins will be used.

## config creator tool
See the [config creator](https://github.com/hannesdelbeke/pyblish-config/tree/main/pyblish_config_creator), a little qt helper tool to help you  create configs. (still in alpha, will have bugs)

# pyblish-plugin-manager

![screenshot](sample/managager_screenshot.JPG)

the plugin manager allows you to override pyblish plugin settings externally. The aim is to assist with pipeline configuration and promote sharing and reusing plugins.

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

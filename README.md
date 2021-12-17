# pyblish-plugin-manager

## overwriting attributes
to make sure your pipeline doesnt break when updating plugins.
pyblish config only overwrites settings it finds in the settings file
it leaves everything else at default value.

example:
a plugin has various attributes. the json only contains a single attribute, node_type = "mesh"
all attributes of the plugin will remain the same except for the node_type.

## explicitly registering plugins
the exception to this is the plugins registered.
it will only use plugins matching the plugin names in the settings file

example:
you have 5 plugins registered. the settings file has 3 plugins listed.
only those 3 plugins will be used.

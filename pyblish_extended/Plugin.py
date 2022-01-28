from pyblish.plugin import *


def actions_from_module(module):
    """Return actions from module

    Arguments:
        module (types.ModuleType): Imported module from which to
            parse valid Pyblish plug-ins.

    Returns:
        List of plug-ins, or empty list if none is found.

    """

    actions = list()

    for name in dir(module):
        if name.startswith("_"):
            continue

        # It could be anything at this point
        obj = getattr(module, name)

        if not inspect.isclass(obj):
            continue

        if not issubclass(obj, Action):
            continue

        ## does not validate if it is a valid action

        # if not plugin_is_valid(obj):
        #     log.debug("Plug-in invalid: %s", obj)
        #     continue

        # if not version_is_compatible(obj):
        #     log.debug("Plug-in %s not compatible with "
        #               "this version (%s) of Pyblish." % (
        #                   obj, __version__))
        #     continue

        # if not host_is_compatible(obj):
        #     log.debug("No supported host found for plugin:%s",  obj)
        #     continue

        actions.append(obj)

    return actions

def actions_from_plugins(plugins):
    """Return actions from plug-ins
    Returns:
        set of plug-ins, or empty set if none is found.
    """
    all_actions = set()
    for plugin in plugins:
        all_actions.add(set(plugin.actions))
    return all_actions

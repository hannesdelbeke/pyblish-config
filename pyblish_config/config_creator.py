import sys
from Qt import QtWidgets
from pyblish import api


skip_attr = ['repair', 'id', 'log', 'process', 'version', 'requires']


def get_plugin_config(plugin):
    # for every plugin, store all settings in the plugin config
    plugin_config = {}
    for attr in dir(plugin):
        if not attr.startswith('_') and attr not in skip_attr:
            value = getattr(plugin, attr)
            plugin_config[attr] = value


def get_project_config_from_discover():
    # get all plugins from pyblish
    plugins = api.discover()

    # store all plugin configs in the pipeline config
    pipeline_config = {}
    for plugin in plugins:
        pipeline_config[plugin.__name__] = get_plugin_config(plugin)

    return pipeline_config


def make_config():
    # get list of all discovered plugins (no filter)
    plugins = api.discover()

    # bake it to a text file / output
    # see default values of properties: actions, accuracy for uv check, order, ....
    # allow to overwrite


    app = QtWidgets.QApplication(sys.argv)
    layout = QtWidgets.QVBoxLayout()

    for plugin in plugins:

        button = QtWidgets.QPushButton(plugin.__name__)
        layout.addWidget(button)

        for attr in dir(plugin):
            if not attr.startswith('_') and attr not in skip_attr:

                layout_attr = QtWidgets.QHBoxLayout()

                w = QtWidgets.QLabel(attr)
                layout_attr.addWidget(w)

                value = getattr(plugin, attr)
                widget = get_widget_from_attr_type(attr, value)

                layout_attr.addWidget(widget)

                layout.addLayout(layout_attr)


    w = QtWidgets.QWidget()
    w.setLayout(layout)

    w.show()
    app.exec_()


def get_widget_from_attr_type(attr, value):
    w = None
    if type(value) == bool:
        w = QtWidgets.QCheckBox()
        w.setChecked(value)
    elif type(value) == int:
        w = QtWidgets.QSpinBox()
        w.setValue(value)
    elif type(value) == int:
        w = QtWidgets.QDoubleSpinBox()
        w.setValue(value)
    elif isinstance(value, str):
        print('a')
        w = QtWidgets.QLabel(value)
    elif isinstance(value, list):
        # TODO special widget that allows to add tags
        s = ''
        for x in value:
            if s:
                s += ', '
            s += str(x)
        w = QtWidgets.QLineEdit(s)

    else:
        w = QtWidgets.QLabel(str(value))
    return w

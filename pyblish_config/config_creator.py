import sys
from Qt import QtWidgets, QtCore
from pyblish import api


skip_attr = ['repair', 'id', 'log', 'process', 'version', 'requires']


def get_plugin_config(plugin):
    # for every plugin, store all settings in the plugin config
    plugin_config = {}
    for attr in dir(plugin):
        if not attr.startswith('_') and attr not in skip_attr:
            value = getattr(plugin, attr)
            plugin_config[attr] = value
    return plugin_config


def get_project_config_from_discover():
    # get all plugins from pyblish
    plugins = api.discover()

    # store all plugin configs in the pipeline config
    pipeline_config = {}
    for plugin in plugins:
        pipeline_config[plugin.__name__] = get_plugin_config(plugin)

    return pipeline_config


class manager_UI(QtWidgets.QWidget):

    def __init__(self, pipeline_config, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.pipeline_config = pipeline_config # todo to init

        self.widget_plugins_list = QtWidgets.QWidget(self)
        self.vbox_plugins = QtWidgets.QVBoxLayout(self)
        self.widget_plugins_list.setLayout(self.vbox_plugins)

        self.hbox = QtWidgets.QHBoxLayout(self)
        self.widget_plugin_config = QtWidgets.QWidget(self)
        self.hbox.addWidget(self.widget_plugin_config)

        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget_plugins_list)

        self.hbox.addWidget(self.scroll)

        # create buttons
        for plugin_name, plugin_config in pipeline_config.items():
            button = QtWidgets.QPushButton(plugin_name, self.widget_plugins_list)
            self.vbox_plugins.addWidget(button)
            button.clicked.connect(self.show_plugin_config)

        self.setLayout(self.hbox)

    def show_plugin_config(self):
        sender = self.sender()
        plugin_name = sender.text()

        # get matching config
        plugin_config = self.pipeline_config[plugin_name]
        w = self.get_plugin_config_widget(plugin_config)

        self.hbox.removeWidget(self.widget_plugin_config)
        self.widget_plugin_config.deleteLater()
        self.widget_plugin_config = None
        # del self.widget_plugin_config

        self.widget_plugin_config = w
        self.hbox.addWidget(w)
        w.repaint()


    def get_plugin_config_widget(self, config):

        plugin_config_widget = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(plugin_config_widget)
        plugin_config_widget.setLayout(vbox)

        for attr, value in config.items():
            layout_attr = QtWidgets.QHBoxLayout(plugin_config_widget)

            w = QtWidgets.QLabel(attr)
            layout_attr.addWidget(w)

            widget = get_widget_from_attr_type(attr, value)
            widget.setParent(plugin_config_widget)

            layout_attr.addWidget(widget)

            vbox.addLayout(layout_attr)

        return plugin_config_widget


def make_config():

    config = get_project_config_from_discover()

    app = QtWidgets.QApplication(sys.argv)

    m = manager_UI(config)
    # m.display_config(config)

    m.show()
    app.exec_()

    return



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

import sys

import pyblish.api
from Qt import QtWidgets, QtCore
from pyblish import api
import json
import copy


skip_attr = ['repair', 'id', 'log', 'process', 'version', 'requires']

# plugin config: the config/settings of a single plugin

# pipeline config: the config/settings of all plugins in your pipeline, a dict of dicts of plugin configs
# since we use names you cant have 2 plugins  with the same name


def get_plugin_config(plugin):
    """
    get all attributes from the plugin class, and save them in a dict
    :param plugin: Pyblish plugin to get settings from
    :return: a dict containing plugin settings
    """
    # for every plugin, store all settings in the plugin config
    plugin_config = {}
    for attr in dir(plugin):
        if not attr.startswith('_') and attr not in skip_attr:
            value = getattr(plugin, attr)
            plugin_config[attr] = value
    plugin_config['__doc__'] = plugin.__doc__
    return plugin_config


def get_pipeline_config_from_discover():
    """
    get all plugin configs from all registered plugins in a single dict
    """
    # get all plugins from pyblish

    #todo set input before we discover. ex host maya
    # or pyblish version, see def plugins_from_module() in pyblish.plugin.py

    # api.register_host('maya')  # todo change this to not rely on maya
    # todo atm some plugins fail because of cannot import cmds from maya, when run from python
    plugins = api.discover()

    # store all plugin configs in the pipeline config
    pipeline_config = {}
    for plugin in plugins:
        pipeline_config[plugin.__name__] = get_plugin_config(plugin)

    return pipeline_config


class manager_UI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.plugin_buttons = []
        self.pipeline_config = {}
        # self.original_pipeline_config = copy.deepcopy(pipeline_config)

        self.json_path_output = r"C:\Projects\pyblish-plugin-manager\output_config.json"
        self.json_path_input = ""

        self.vbox_config_layout = QtWidgets.QVBoxLayout(self)  # this needs to happen before scrollarea
        self.hbox_main_layout = QtWidgets.QHBoxLayout(self)  # this needs to happen before scrollarea
        self.config_button_layout = QtWidgets.QHBoxLayout()
        self.scroll = self.create_widget_plugins_scroll_area()

        self.widget_plugin_config = QtWidgets.QWidget(self)
        # self.hbox.addWidget(self.scroll)
        # self.vbox_config_layout.addLayout(self.hbox)
        # self.vbox_config_layout.addLayout(self.config_button_layout)

        self.config_main_widget = QtWidgets.QWidget()
        self.config_main_widget.setLayout(self.vbox_config_layout)

        self.load_config_button = QtWidgets.QPushButton('load_config')
        self.save_config_button = QtWidgets.QPushButton('save_config')
        # self.load_config_button.clicked.connect(self.show_plugin_config)
        self.save_config_button.clicked.connect(self.save_project_config)

        self.config_button_layout.addWidget(self.load_config_button)
        self.config_button_layout.addWidget(self.save_config_button)

        self.vbox_config_layout.addWidget(self.scroll)
        self.vbox_config_layout.addLayout(self.config_button_layout)

        # self.hbox_main_layout.addLayout(self.vbox_config_layout)
        self.hbox_main_layout.addWidget(self.config_main_widget)
        self.hbox_main_layout.addWidget(self.widget_plugin_config)

        # self.vbox_main_layout.addWidget(self.config_buttons_widget)

        self.setLayout(self.hbox_main_layout)

    def show_plugin_settings(self):
        # display  plugin settings from first plugin, prevents a weird layout change
        if self.plugin_buttons:
            plugin_name = self.plugin_buttons[0].text()
            self.show_plugin_config(plugin_name)

    def show_clicked_plugin_config(self, *args):
        sender = self.sender()
        plugin_name = sender.text()
        self.show_plugin_config(plugin_name)

    def show_plugin_config(self, plugin_name):
        """
        handle all the fluff around showing a new plugin config widget, and create it
        :param plugin_name: name of the plugin
        :return: Qt widget visualising the plugin config
        """

        # get matching config
        plugin_config = self.pipeline_config[plugin_name]
        w = self.create_widget_plugin_config(plugin_config, plugin_name)

        self.hbox_main_layout.removeWidget(self.widget_plugin_config)
        self.widget_plugin_config.deleteLater()
        self.widget_plugin_config = None
        # del self.widget_plugin_config

        self.widget_plugin_config = w
        self.hbox_main_layout.addWidget(w)
        w.repaint()

    def load_config(self, pipeline_config):
        self.original_pipeline_config = copy.deepcopy(pipeline_config)
        self.pipeline_config = copy.deepcopy(pipeline_config)  # pipeline_config
        self.delete_plugin_buttons()
        self.create_widget_plugin_buttons()
        self.show_plugin_settings()


    def create_widget_plugins_scroll_area(self):
        self.widget_plugins_list = QtWidgets.QWidget(self)
        self.vbox_plugins = QtWidgets.QVBoxLayout(self)
        self.widget_plugins_list.setLayout(self.vbox_plugins)

        self.scroll = QtWidgets.QScrollArea(self)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget_plugins_list)

        # self.create_plugin_buttons()

        return self.scroll

    def create_widget_plugin_buttons(self):
        for plugin_name, plugin_config in self.pipeline_config.items():

            w = QtWidgets.QCheckBox()
            w.setChecked(True)
            # signal_func = w.stateChanged

            button = QtWidgets.QPushButton(plugin_name, self.widget_plugins_list)
            button.clicked.connect(self.show_clicked_plugin_config)
            self.plugin_buttons.append(button)

            layout = QtWidgets.QHBoxLayout(self)
            layout.addWidget(w)
            layout.addWidget(button)

            self.vbox_plugins.addLayout(layout)

        self.vbox_plugins.addStretch()  # add stretch on bottom to push all buttons to top instead of center

    def create_widget_plugin_config(self, plugin_config, plugin_name):
        """
        create a widget for the plugin config

        ------------------- -------------------
        | attribute_1_name | attribute_1_value |
        | attribute_2_name | attribute_2_value |
        | ...              | ...               |
        ------------------- -------------------

        :param plugin_config:
        :param plugin_name:
        :return: the plugin config widget
        """

        # todo show visual difference default values vs editted
        # todo add reset to default settings button

        plugin_config_widget = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(plugin_config_widget)
        plugin_config_widget.setLayout(vbox)

        self.current_plugin_name = plugin_name
        w = QtWidgets.QLabel(plugin_name)  # get name plugin
        vbox.addWidget(w)

        self.plugin_config_widgets = []
        for attribute_name, attribute_value in plugin_config.items():  # for every attribute

            # WIDGET 1: create a widget containing the value
            widget = self.create_widget_from_attr_type(attribute_name, attribute_value)
            if not widget:
                continue  # skip unsupported types

            self.plugin_config_widgets.append(widget)

            widget.setObjectName('attr_widget_' + attribute_name)  # not used but nice to name your widgets
            widget.setProperty('attribute_name', attribute_name)  # store the attribute name in the widget
            # TODO data passed by name, add support for plugins with same name

            # WIDGET 2: create widget for the attribute name
            attribute_name_label = QtWidgets.QLabel(attribute_name)

            # layout widgets next each other
            layout_attr = QtWidgets.QHBoxLayout(plugin_config_widget)
            layout_attr.addWidget(attribute_name_label)
            layout_attr.addWidget(widget)
            vbox.addLayout(layout_attr)

        vbox.addStretch()

        return plugin_config_widget

    # def update_plugin_config_value(self):
    #     sender = self.sender()
    #     plugin_name = sender.parent

    def create_widget_from_attr_type(self, attr, value):
        """
        decide which widget to use based on the attribute type
        :param attr:
        :param value:
        :return:
        """
        w = None
        signal_func = None  # state to connect too
        if type(value) is bool:
            w = QtWidgets.QCheckBox()
            w.setChecked(value)
            signal_func = w.stateChanged

        elif type(value) is int:
            w = QtWidgets.QSpinBox()
            w.setValue(value)
            signal_func = w.valueChanged

        elif type(value) is float:
            w = QtWidgets.QDoubleSpinBox()
            w.setValue(value)
            signal_func = w.valueChanged

        elif isinstance(value, str):
            w = QtWidgets.QLineEdit(value)
            signal_func = w.textChanged

        elif isinstance(value, list):
            # list to comma separated string
            value_str = ''
            for x in value:
                if value_str:
                    value_str += ','
                value_str += str(x)
            w = QtWidgets.QLineEdit(value_str)


            # remember the type so we can convert the string back to the original type
            # see get_value_from_widget
            # w.setProperty('attr_type', type(value[0]))

            # todo we cant recognise the type if the list is empty. bug!

            signal_func = w.textChanged


        #     # todo ideally run recursive if list
        #     # TODO special widget that allows to add tags
        #     s = ''
        #     for x in value:
        #         if s:
        #             s += ', '
        #         s += str(x)
        #
        #     w = QtWidgets.QLineEdit(s)
        #     signal_func = w.textChanged

        elif isinstance(value, pyblish.api.Plugin):
            pass
            # w = QtWidgets.QLabel(value)

        elif isinstance(value, pyblish.api.Action):  # todo support list of actions
            pass
            # w = QtWidgets.QLabel(value)

        elif callable(value):  # skip functions
            pass

        else:
            w = QtWidgets.QLabel(str(value))

        if signal_func:
            signal_func.connect(self.set_plugin_config_from_widget)
        return w  # signal_func

    # todo create special widget for build in pyblish attributes.
    # example: match should not be a int, but a dropdown with following values:
    #     Subset,
    #     Intersection,
    #     Exact,

    # order: (but also option to override)
    # values set in pylblish.plugin.
    #     CollectorOrder,
    #     ValidatorOrder,
    #     ExtractorOrder,
    #     IntegratorOrder,

    # add support to hookup actions
    # actions display comma separated with their IDENTIFIER attribute
    # we want to allow costumising multiple action configs, of the same action


    def set_plugin_config_from_widget(self):
        # get current plugin config
        config = self.pipeline_config[self.current_plugin_name]

        for widget in self.plugin_config_widgets:
            attribute_name = widget.property('attribute_name')
            # attr_name = widget.parent().text()  # get parent labels text, this is the attribute name
            attr_value = self.get_value_from_widget(widget)
            if attr_value is not None:
                config[attribute_name] = attr_value

    def delete_plugin_buttons(self):
        for button in self.plugin_buttons:
            button.deleteLater()

    def get_value_from_widget(self, widget):
        """ helper function to get the value from any type of widget """
        if type(widget) is QtWidgets.QCheckBox:
            return widget.checkState() == QtCore.Qt.Checked
        if type(widget) in (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox):
            return widget.value()
        if type(widget) is QtWidgets.QLineEdit:
            # if commas in text, convert to list
            text = widget.text()
            if ',' in text:
                return text.split(',')
            # todo convert to right value
            else:
                return text

    # def load_project_config(self):
    #     """
    #     load UI settings from a json settings file
    #     """
    #     with open(self.json_path_output, 'w', encoding='utf-8') as f:
    #         json.dump(config_data, f, indent=4)
    #     config_data = {}
    #     for k, v in self.pipeline_config.items():
    #         # if self.original_pipeline_config[k] != v:
    #         config_data[k] = {}
    #
    #         for k2, v2 in v.items():
    #             if self.original_pipeline_config[k][k2] != v2:
    #                 config_data[k][k2] = v2

    def save_project_config(self):
        """
        save UI settings into a json settings file
        """

        # get differences between config and plugin settings
        # todo fix that
        #  naively assume differences can be calc between configs
        #  this wont work if we edit an already different config

        # this diff is only needed when doing register_plugin -> discover -> plugins ->config
        # when we edit an alrdy existing config we dont need to do any diffing

        config_data = {}
        for k, v in self.pipeline_config.items():
            # if self.original_pipeline_config[k] != v:
            config_data[k] = {}

            for k2, v2 in v.items():
                if self.original_pipeline_config[k][k2] != v2:
                    config_data[k][k2] = v2

            # config_data[k] = v

        # set(self.pipeline_config)
        # print(set(self.pipeline_config))
        # print(self.pipeline_config)
        # print(list(self.pipeline_config.items()))
        # set(self.pipeline_config.items())
        # difference = set(self.pipeline_config.items()) ^ set(self.original_pipeline_config.items())
        # config_data = dict(difference)


        # save self.pipeline_config to json
        with open(self.json_path_output, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)


# todo would be cool if pipeline didnt just filter but also saved locations to paths of plugins


def make_config():

    config = get_pipeline_config_from_discover()

    app = QtWidgets.QApplication(sys.argv)

    m = manager_UI()
    m.load_config(config)

    # m.display_config(config)

    m.show()
    app.exec_()

# ideally all this make config stuff happens using default settings.
# user just runs a single or 2 commands and it all runs

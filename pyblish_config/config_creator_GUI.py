import sys

import pyblish.api
from Qt import QtWidgets, QtCore
from Qt.QtWidgets import QFileDialog

import copy

from . import config
from .config import get_pipeline_config_from_plugins


class plugin_widget(object):
    def __init__(self, pyblish_plugin, widget):
        # object.__init__(self)

        self.name = ""



default_plugin_attributes = ['actions', 'active', 'families', 'order', 'plugin', 'hosts', 'label', 'match', 'optional',
                      'targets', 'version', 'requires', 'log', 'id', 'repair']
# todo read these from plugin class directly


class manager_UI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.pipeline_config = {}
        self.json_path_output = r"C:\Projects\pyblish-plugin-manager\output_config.json"  # todo remove hardcoded path
        self.json_path_input = ""

        # create plugins list widget and layout
        self.widgets_plugin_buttons = []
        self.widget_plugins_list = self.create_left()   # the scroll list that contains the plugin buttons

        # create plugin settings widget
        # self.widget_plugin_config_container_main = self.create_right()  # sets up more self. variables inside method

        # # create placeholder
        self.widget_plugin_config = QtWidgets.QWidget(self)

        # Layout left and right widgets
        self.hbox_main_layout = QtWidgets.QHBoxLayout(self)
        self.hbox_main_layout.addWidget(self.widget_plugins_list)  # self.config_main_widget
        # self.hbox_main_layout.addWidget(self.widget_plugin_config_container_main)  # self.widget_plugin_config

        # self.vbox_main_layout.addWidget(self.config_buttons_widget)

        self.setLayout(self.hbox_main_layout)

    def create_left(self):

        self.vbox_config_layout = QtWidgets.QVBoxLayout(self)  # this needs to happen before scrollarea
        # create widget, apply layout, add widgets to layout.

        # create config widget
        widget = QtWidgets.QWidget()
        widget.setLayout(self.vbox_config_layout)

        w = QtWidgets.QWidget(self)
        self.vbox_plugins = QtWidgets.QVBoxLayout(self)
        w.setLayout(self.vbox_plugins)

        # self.config_button_layout = QtWidgets.QHBoxLayout()
        # self.config_button_layout.addWidget(self.load_config_button)
        # self.config_button_layout.addWidget(self.save_config_button)
        #
        # create scroll area
        widget_scroll = self.wrap_widget_in_scroll_area(w)

        # create config buttons
        # self.register_plugins_button = QtWidgets.QPushButton('register plugins')
        self.load_config_button = QtWidgets.QPushButton('load config')
        self.save_config_button = QtWidgets.QPushButton('save config')
        self.load_config_button.clicked.connect(self.load_project_config)
        self.save_config_button.clicked.connect(self.save_project_config)

        self.config_button_layout = QtWidgets.QHBoxLayout()
        # self.config_button_layout.addWidget(self.register_plugins_button)
        self.config_button_layout.addWidget(self.load_config_button)
        self.config_button_layout.addWidget(self.save_config_button)

        # dropdown = QtWidgets.QComboBox()
        # dropdown.addItems(['register plugins', 'configure pipeline'])

        # self.vbox_config_layout.addWidget(dropdown)
        self.vbox_config_layout.addWidget(widget_scroll)
        self.vbox_config_layout.addLayout(self.config_button_layout)

        return widget

    def _open_qfiledialog(self):
        """
        Used to browse to the save location for the config
        """
        title = "save config file"
        file_types = "Json (*.json)"
        root_folder = ""
        return QtWidgets.QFileDialog.getOpenFileName(self, title, root_folder, file_types)[0]


    def show_config_first_plugin(self):
        # display  plugin settings from first plugin, prevents a weird layout change
        if self.widgets_plugin_buttons:
            plugin_name = self.widgets_plugin_buttons[0].text()
            self.show_plugin_config(plugin_name)

    def refresh_attributes(self):
        # toggle hide default pyblish attributes

        show_pyblish_attr = self.hide_pyblish_attributes_widget.checkState() != QtCore.Qt.Checked


        for widget in self.current_plugin_attributes_widgets:
            attribute_name = widget.property('attribute_name')
            attribute_container_widget = widget.property('attribute_container_widget')

            if attribute_name in default_plugin_attributes:
                attribute_container_widget.setVisible(show_pyblish_attr)

            # widget.setVisible(not widget.isVisible())

    def show_clicked_plugin_config(self, *args):
        sender = self.sender()
        plugin_name = sender.text()
        self.show_plugin_config(plugin_name)

    def show_plugin_config(self, plugin_name):
        """
        handle all the fluff around showing a new plugin config widget, and create it, delete the old one
        :param plugin_name: name of the plugin
        :return: Qt widget visualising the plugin config
        """

        # get matching config
        plugin_config = self.pipeline_config[plugin_name]
        w = self.create_widget_plugin_config(plugin_config, plugin_name)

        # delete old widget
        self.hbox_main_layout.removeWidget(self.widget_plugin_config)
        self.widget_plugin_config.deleteLater()
        self.widget_plugin_config = None

        self.widget_plugin_config = w
        self.hbox_main_layout.addWidget(self.widget_plugin_config)
        w.repaint()

        self.color_attribute_widgets()

    def load_config(self, pipeline_config):
        self.original_pipeline_config = copy.deepcopy(pipeline_config)
        self.pipeline_config = copy.deepcopy(pipeline_config)  # pipeline_config

        # plugin screen
        self.delete_plugin_buttons()
        self.create_widget_plugin_buttons()

        # config screen
        self.show_config_first_plugin()

    def wrap_widget_in_scroll_area(self, widget):
        """
        wrap a widget in a scroll area
        :param widget: widget to be wrapped
        :return: scroll area containing the widget
        """
        scroll = QtWidgets.QScrollArea(self)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        return scroll

    def create_widget_plugin_buttons(self):
        for plugin_name, plugin_config in self.pipeline_config.items():

            w = QtWidgets.QCheckBox()
            w.setChecked(True)
            # signal_func = w.stateChanged

            button = QtWidgets.QPushButton(plugin_name, self.widget_plugins_list)
            button.clicked.connect(self.show_clicked_plugin_config)
            self.widgets_plugin_buttons.append(button)

            layout = QtWidgets.QHBoxLayout(self)
            layout.addWidget(w)
            layout.addWidget(button)

            self.vbox_plugins.addLayout(layout)

        self.vbox_plugins.addStretch()  # add stretch on bottom to push all buttons to top instead of center

    def create_widget_plugin_config(self, plugin_config, plugin_name):
        """
        create the setting screen for the plugin you selected

        ------------------- -------------------
        | attribute_1_name | attribute_1_value |
        | attribute_2_name | attribute_2_value |
        | ...              | ...               |
        ------------------- -------------------

        :param plugin_config:
        :param plugin_name:
        :return: the plugin config widget
        """
        self.current_plugin_name = plugin_name

        # create main container
        plugin_config_main_widget = QtWidgets.QWidget()
        plugin_config_main_layout = QtWidgets.QVBoxLayout(self)
        plugin_config_main_widget.setLayout(plugin_config_main_layout)

        # create second container: attributes_scroll_layout
        widget_container2 = QtWidgets.QWidget()
        attributes_scroll_layout = QtWidgets.QVBoxLayout(self)
        widget_container2.setLayout(attributes_scroll_layout)
        # wrap the second container in a scroll area
        widget_scroll = self.wrap_widget_in_scroll_area(widget_container2)

        # todo show visual difference default values vs editted, see self.color_widget
        # todo add reset to default settings button

        # create title and doc widget
        widget_plugin_config_title = QtWidgets.QLabel("PLUGIN NAME: " + plugin_name)
        widget_plugin_config_title.setStyleSheet("font-size: 16px;")
        doc_string = str(plugin_config.get('__doc__', '')).strip()
        self.widget_plugin_doc = QtWidgets.QLabel(doc_string)
        # layout = QtWidgets.QVBoxLayout(self)
        # self.widget_plugin_doc.setLayout(layout)
        # layout.setMargin(0)

        doc_scroll_widget = self.wrap_widget_in_scroll_area(self.widget_plugin_doc)
        doc_scroll_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        doc_scroll_widget.setMaximumHeight(100)

        # create checkbox hide pyblish attributes
        self.hide_pyblish_attributes_widget = QtWidgets.QCheckBox("Hide Pyblish attributes")
        self.hide_pyblish_attributes_widget.stateChanged.connect(self.refresh_attributes)

        # add title, doc, and scroll widgets to main container
        plugin_config_main_layout.addWidget(widget_plugin_config_title)
        plugin_config_main_layout.addWidget(doc_scroll_widget)
        plugin_config_main_layout.addWidget(widget_scroll)
        plugin_config_main_layout.addWidget(self.hide_pyblish_attributes_widget)

        # create attribute widgets
        self.current_plugin_attributes_widgets = []  # list of attribute widgets
        for attribute_name, attribute_value in plugin_config.items():  # for every attribute

            # hide_pyblish_attr = self.hide_pyblish_attributes_widget.checkState() == QtCore.Qt.Checked
            # if hide_pyblish_attr and attribute_name in default_plugin_attributes:
            #     continue


            # WIDGET 1: create a widget containing the value
            attribute_widget = self.create_widget_from_attribute(attribute_name, attribute_value)

            if not attribute_widget:
                continue  # skip unsupported types

            self.add_tooltips(attribute_widget, attribute_name)
            if attribute_name not in default_plugin_attributes:
                self.add_tooltips(attribute_widget, attribute_name, plugin_config['__doc__'])

            attribute_widget.setObjectName('attr_widget_' + attribute_name)  # not used but nice to name your widgets
            attribute_widget.setProperty('attribute_name', attribute_name)  # store the attribute name in the widget
            # TODO data passed by name, add support for plugins with same
            self.current_plugin_attributes_widgets.append(attribute_widget)

            # WIDGET 2: create widget for the attribute name
            attribute_name_label = QtWidgets.QLabel(attribute_name)

            # layout widgets next each other
            layout_attr = QtWidgets.QHBoxLayout(plugin_config_main_widget)

            attr_widget_container = QtWidgets.QWidget()
            attr_widget_container.setLayout(layout_attr)
            attribute_widget.setProperty('attribute_container_widget', attr_widget_container)

            layout_attr.addWidget(attribute_name_label)
            layout_attr.addWidget(attribute_widget)
            layout_attr.setMargin(0)
            # Todo link widget to label and plugin parent widget (button)


            attributes_scroll_layout.addWidget(attr_widget_container)

            # todo WIP buttons to change type for attribute, incase we cant find type from value. ex. empty value.
            # change_type_button = QtWidgets.QPushButton('change type')
            # type_button = QtWidgets.QPushButton(str(type(attribute_value)))
            # layout_attr.addWidget(change_type_button)
            # layout_attr.addWidget(type_button)

        attributes_scroll_layout.addStretch()

        self.hide_pyblish_attributes_widget.setChecked(True) # do this at the end, it triggers a refresh

        return plugin_config_main_widget

    def color_attribute_widgets(self):
        any_value_changed = False
        for w in self.current_plugin_attributes_widgets:
            value_changed = self._color_attribute_widget(w)
            any_value_changed = any_value_changed or value_changed

        if any_value_changed:
            pass

    def _color_widget(self, widget, value_changed):
        if value_changed:
            widget.setStyleSheet("background-color: rgb(255, 200, 100);")
        else:
            widget.setStyleSheet("")

    def _color_attribute_widget(self, attribute_widget):
        # color the widget and the matching plugin

        # dont color labels, you cant change their values
        if type(attribute_widget) == QtWidgets.QLabel:
            return False

        original_config = self.original_pipeline_config[self.current_plugin_name]

        attribute_name = attribute_widget.property('attribute_name')
        attribute_value = self.get_value_from_widget(attribute_widget)

        # todo this doesnt aply when swapping plugin config screens
        # todo color the plugin button too (parent)
        # color widget when changed
        original_value = original_config[attribute_name]
        value_changed = original_value != attribute_value

        self._color_widget(attribute_widget, value_changed)
        # todo set label to red isntead of widget

        return value_changed

    def color_plugin_widgets(self):
        for plugin_widget in self.widgets_plugin_buttons:

            # check if value changed
            value_changed = False

            plugin_name = plugin_widget.text()
            original_config = self.original_pipeline_config[plugin_name]
            current_config = self.pipeline_config[plugin_name]

            for key, value in current_config.items():
                if original_config[key] != value:
                    value_changed = True
                    # print(key, original_config[key], value)
                    break

            self._color_widget(plugin_widget, value_changed)

    def create_widget_from_attribute(self, attr_name, attr_value):
        """
        Create a widget to edit the attribute.
        Add the attribute name to the widget as a property: attribute_name
        """
        # todo handle exceptions

        if attr_name.lower() == 'actions':
            return QtWidgets.QLabel(str(attr_value))  # return default widget

        widget = self.create_widget_from_attr_type(attr_value)



        return widget

    def add_tooltips(self, w, name, pyblish_plugin_doc=0):
        """
        Add tooltips to widgets
        :param w:
        :param name:
        :param pyblish_plugin_doc: if not provided, will try to get base pyblish docstring from pyblish.plugin.Plugin.__doc__
        :return:
        """

        if not pyblish_plugin_doc:
            return

        # todo we do a lot of stuff here, save the calculations so we only do this once and not for every attr.
        #  also only do this for pyblish attributes
        if pyblish_plugin_doc == 0:
            pyblish_plugin_doc = pyblish.plugin.Plugin.__doc__
        attribute_doc_raw = pyblish_plugin_doc.split('Attributes:')[1]
        # check if next line contains 1 or 2 tabs. 2 tabs continue doc, 1 line stop doc and start next attribute doc
        attribute_doc_raw_split = attribute_doc_raw.split('        ')
        # if it starts with 1 tab add it to the previous entry and delete current entry
        index = -1
        for x in attribute_doc_raw_split:
            index += 1
            if x.startswith('    '):
                attribute_doc_raw_split[index - 1] += x[4:]  # remove 1 tab at start and add to previous entry
                attribute_doc_raw_split[index] = ''
        # sort doc entries by attribute name in a dict
        attribute_doc = {}
        for x in attribute_doc_raw_split:
            if x and ':' in x:
                # before the : is the attribute name, after is the docstring, split 1 since doc could contain :
                attribute_name = x.split(':', 1)[0].strip()
                # handle space in attr name: 'attr_name (str) : docstring'
                attribute_name = attribute_name.split(' ',1)[0]
                attribute_doc[attribute_name] = x.split(':', 1)[1].strip()
        if name in attribute_doc.keys():
            w.setToolTip(attribute_doc[name])

    def create_widget_from_attr_type(self, value):
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
                if len(value_str) > 1:
                    value_str += ','
                value_str += str(x)
            w = QtWidgets.QLineEdit(value_str)
            signal_func = w.textChanged

            # remember the type so we can convert the string back to the original type
            # see get_value_from_widget
            # w.setProperty('attribute_type', type(value))
            # todo we cant recognise the type if the list is empty. bug!


        #     # todo ideally run recursive if list
        #     # TODO special widget that allows to add tags


        elif isinstance(value, pyblish.api.Plugin):
            pass
            # w = QtWidgets.QLabel(value)

        elif isinstance(value, pyblish.api.Action):  # todo support list of actions
            pass
            # w = QtWidgets.QLabel(value)

        elif callable(value):  # skip functions
            pass

        else:
            w = QtWidgets.QLabel(str(value))  # return default widget

        if w:
            w.setProperty('attribute_type', type(value))

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
    # actions display comma separated TODO
    # we want to allow costumising multiple action configs, of the same action

    # actions are meta plugins.
    # we can use create plugin config widget to create a widget for each action
    # we need to allow user to add and remove multiple actions

    # current discovered actions
    # browse to folder with new actions

    # TODO type from attr cant be found when default value is None.
    # this results in no support to change the widget value for this attribute
    # ex. when label is None, we cant change the value of the label.
    # allow user to overwrite the type of the attribute
    # how can we add support for all types? including lists and dicts of types, and lists of lists of lists ...

    def set_plugin_config_from_widget(self):
        """
        this function runs when changing an attribute widget,
        for every attribute widget of the current plugin,
        we get the value and save it in the config dict: self.pipeline_config
        """
        # get current plugin config
        config = self.pipeline_config[self.current_plugin_name]  # todo move to getter setter

        for attribute_widget in self.current_plugin_attributes_widgets:
            attribute_name = attribute_widget.property('attribute_name')  # todo move this to a class, objOriented setup
            # attr_name = widget.parent().text()  # get parent labels text, this is the attribute name
            attribute_value = self.get_value_from_widget(attribute_widget)
            if attribute_value is not None:  # todo will bug if value is supposed to be None in settings
                # save value from widget in the config
                config[attribute_name] = attribute_value

        self.color_attribute_widgets()  # update colors when changing the widget
        self.color_plugin_widgets()

    def delete_plugin_buttons(self):
        for button in self.widgets_plugin_buttons:
            button.deleteLater()

    def get_value_from_widget(self, widget):
        """ helper function to get the value from any type of widget """

        # get value from widget
        value = None  # todo will bug if value is none on purpose in the config
        if type(widget) is QtWidgets.QCheckBox:
            value = widget.checkState() == QtCore.Qt.Checked
        if type(widget) in (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox):
            value = widget.value()
        if type(widget) is QtWidgets.QLineEdit:
            # if commas in text, convert to list
            text = widget.text()
            value = text

        # convert value to right format / type
        value_type = widget.property('attribute_type')
        if value_type is list:
            value = text.split(',')

        return value

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

        # get path
        browsed_path = self._open_qfiledialog().replace("/", "\\")
        if browsed_path:
            self.json_path_output = browsed_path

        config_data = config.diff_pipeline_configs(self.pipeline_config, self.original_pipeline_config)
        config.save_config(self.json_path_output, config_data)

    def load_project_config(self):
        # browse to config

        title = "save config file"
        file_types = "Json (*.json)"
        root_folder = ""
        browsed_path = QFileDialog.getOpenFileName(self, title, root_folder, file_types)[0].replace("/", "\\")
        # browsed_path = self._open_qfiledialog().replace("/", "\\")
        # if browsed_path:
        #     self.json_path_output = browsed_path

        # open config
        self.pipeline_config = config.load_config(browsed_path)  # todo verify the loaded config is valid

        # refresh colors
        self.color_attribute_widgets()
        self.color_plugin_widgets()

        # todo handle case where the discover does not contain plugin but the config does, same with attributes
        # ex discover returns plugin 1 and 2, but config also contains settings for plugin 3
        # might not be returned because it has a compile error since a recent update


# todo would be cool if pipeline didnt just filter but also saved locations to paths of plugins



def make_config(discover=True, config=None):
    if discover:

        # get all plugins from pyblish

        # support creating a pipeline for specific hosts. ex a maya pipeline
        # todo set input before we discover. ex host maya
        # or pyblish version, see def plugins_from_module() in pyblish.plugin.py

        # api.register_host('maya')  # todo change this to not rely on maya
        # todo atm some plugins fail because of cannot import cmds from maya, when run from python

        plugins = pyblish.api.discover()
        config = get_pipeline_config_from_plugins(plugins)

    app = QtWidgets.QApplication(sys.argv)

    m = manager_UI()
    m.load_config(config)
    m.setWindowTitle('pyblish pipeline manager')
    # m.display_config(config)

    m.show()
    app.exec_()

# ideally all this make config stuff happens using default settings.
# user just runs a single or 2 commands and it all runs


# action management
# actions get hooked up in code
# there is no discover phase for actions
# register / store actions somewhere
# an action is a plugin
# plugins can be discovered and registered
# plugins are classes
# plugins can be discovered by module/module_path, by class/instance/plugin_name


# Pyblish says:
#   action: User-supplied interactive action
#   plugin: Base-class for plugins

# but what is a plugin? a method that has meta data and gets called by the pipeline in certain conditions
# collect, validate, publish, integrate... all "actions" taken in certain conditions
# a plugin is a class that has a method called run, that takes this action

# the main difference is: actions and plugins are used in different situations, and they contain different metadata
# but they're mostly the same
# so we can treat them the same, share UI config widgets, etc
# an action can work on the plugin instance, and it's data

# lets say simple action: delete node: mesh/object/material
# runs on nodes found by the plugin




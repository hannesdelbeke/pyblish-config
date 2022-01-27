import sys

import pyblish.api
from Qt import QtWidgets, QtCore
from Qt.QtWidgets import QFileDialog

import copy

from pyblish_config import config
from pyblish_config.config import get_pipeline_config_from_plugins

SUPPORTED_TYPES = [int, float, str, bool, list, dict, tuple, type(None), ]


def wrap_widget_in_scroll_area(parent, widget):
    """
    wrap a widget in a scroll area
    :param widget: widget to be wrapped
    :return: scroll area containing the widget
    """
    scroll = QtWidgets.QScrollArea(parent)
    scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    scroll.setWidgetResizable(True)
    scroll.setWidget(widget)

    return scroll

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
        self.hide_pyblish_attributes = True

        # create plugins list widget and layout
        self.widgets_plugin_buttons = []
        self.widget_plugins_list = self.pipeline_config_create_plugin_list()   # the scroll list that contains the plugin buttons
        self.widget_plugins_list.setMinimumWidth(200)
        self.widget_plugins_list.setMaximumWidth(200)
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

    # pipeline config

    def pipeline_config_create_plugin_list(self):

        self.vbox_config_layout = QtWidgets.QVBoxLayout(self)  # this needs to happen before scrollarea
        # create widget, apply layout, add widgets to layout.

        # create config widget
        widget = QtWidgets.QWidget()
        widget.setLayout(self.vbox_config_layout)

        plugin_button_container_widget = QtWidgets.QWidget(self)
        self.vbox_plugins = QtWidgets.QVBoxLayout(self)
        plugin_button_container_widget.setLayout(self.vbox_plugins)

        # self.config_button_layout = QtWidgets.QHBoxLayout()
        # self.config_button_layout.addWidget(self.load_config_button)
        # self.config_button_layout.addWidget(self.save_config_button)
        #
        # create scroll area
        widget_scroll = wrap_widget_in_scroll_area(self, plugin_button_container_widget)

        # create config buttons
        # self.register_plugins_button = QtWidgets.QPushButton('register plugins')
        self.load_config_button = QtWidgets.QPushButton('load config')
        self.save_config_button = QtWidgets.QPushButton('save config')
        self.load_config_button.clicked.connect(self.pipeline_config_browse_and_load)
        self.save_config_button.clicked.connect(self.pipeline_config_browse_and_save)

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

    def pipeline_config_refresh_active_checkboxes(self):
        # todo atm this method runs several times, optimise and only run once for each plugin
        for w in self.widgets_plugin_checkboxes:
            plugin_name = w.property('plugin_name')
            is_active = self.pipeline_config[plugin_name]['active']
            w.setChecked(is_active)

    def pipeline_config_plugin_buttons_create_widget(self):
        self.widgets_plugin_checkboxes = []
        for plugin_name, _ in self.pipeline_config.items():

            plugin_active_checkbox_widget = QtWidgets.QCheckBox()
            plugin_active_checkbox_widget.stateChanged.connect(self.pipeline_config_toggle_plugin_active)
            plugin_active_checkbox_widget.setProperty('plugin_name', plugin_name)

            self.widgets_plugin_checkboxes.append(plugin_active_checkbox_widget)
            # signal_func = w.stateChanged
            # w.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

            button = QtWidgets.QPushButton(plugin_name, self.widget_plugins_list)
            button.clicked.connect(self.plugin_config_show_clicked)
            self.widgets_plugin_buttons.append(button)
            # button.setCenterAlignment()
            # button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

            layout = QtWidgets.QHBoxLayout(self)
            layout.addWidget(plugin_active_checkbox_widget, 0)
            layout.addWidget(button)
            layout.addStretch()
            # layout.setStretch(0, 0)
            self.vbox_plugins.addLayout(layout)
        self.pipeline_config_refresh_active_checkboxes()
        self.vbox_plugins.addStretch()  # add stretch on bottom to push all buttons to top instead of center

    def pipeline_config_toggle_plugin_active(self):
        sender = self.sender()
        plugin_name = sender.property('plugin_name')
        self.pipeline_config[plugin_name]['active'] = sender.checkState() == QtCore.Qt.Checked

        # trigger redraw of plugin config
        self.plugin_config_show(plugin_name)

        # refresh colors
        self.plugin_config_color_attribute_widgets()
        self.pipeline_config_color_plugin_widgets()


    def pipeline_config_delete_plugin_buttons(self):
        for button in self.widgets_plugin_buttons:
            button.deleteLater()

    def pipeline_config_browse_and_save(self):
        """
        save UI settings into a json settings file
        """

        # get path
        browsed_path = self._open_qfiledialog().replace("/", "\\")
        if browsed_path:
            self.json_path_output = browsed_path

        # todo fix that
        #  naively assume differences can be calc between configs
        #  this wont work if we edit an already different config
        # this diff is only needed when doing register_plugin -> discover -> plugins ->config
        # when we edit an alrdy existing config we dont need to do any diffing
        config_data = config.diff_pipeline_configs(self.pipeline_config, self.original_pipeline_config)

        config.save_config_as_json(self.json_path_output, config_data)

    def pipeline_config_browse_and_load(self):
        # browse to config

        title = "save config file"
        file_types = "Json (*.json)"
        root_folder = ""
        browsed_path = QFileDialog.getOpenFileName(self, title, root_folder, file_types)[0].replace("/", "\\")
        # browsed_path = self._open_qfiledialog().replace("/", "\\")
        # if browsed_path:
        #     self.json_path_output = browsed_path

        # open config

        ## Raw loading of config
        # self.pipeline_config = config.load_config(browsed_path)  # todo verify the loaded config is valid

        ## additive loading of config
        loaded_config = config.load_config_from_json(browsed_path)
        for plugin_name, plugin_config in loaded_config.items():
            for attr_name, value in plugin_config.items():
                self.pipeline_config[plugin_name][attr_name] = value

        # refresh colors
        self.plugin_config_color_attribute_widgets()
        self.pipeline_config_color_plugin_widgets()

        # todo handle case where the discover does not contain plugin but the config does, same with attributes
        # ex discover returns plugin 1 and 2, but config also contains settings for plugin 3
        # might not be returned because it has a compile error since a recent update

    def pipeline_config_refresh(self):
        self.pipeline_config_delete_plugin_buttons()
        self.pipeline_config_plugin_buttons_create_widget()

    def pipeline_config_load(self, pipeline_config):
        self.original_pipeline_config = copy.deepcopy(pipeline_config)
        self.pipeline_config = copy.deepcopy(pipeline_config)  # pipeline_config

        # plugin screen
        self.pipeline_config_refresh()

        # config screen
        self.plugin_config_show_first()

    def pipeline_config_color_plugin_widgets(self):
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

    # plugin config

    def plugin_config_show_first(self):
        # display  plugin settings from first plugin, prevents a weird layout change
        if self.widgets_plugin_buttons:
            plugin_name = self.widgets_plugin_buttons[0].text()
            self.plugin_config_show(plugin_name)

    def plugin_config_refresh_attributes(self):
        """
        toggle hide default pyblish attributes
        """

        self.hide_pyblish_attributes = self.hide_pyblish_attributes_widget.checkState() == QtCore.Qt.Checked
        show_pyblish_attr = not self.hide_pyblish_attributes

        for widget in self.current_plugin_attributes_widgets:
            attribute_name = widget.property('attribute_name')
            row_index = widget.property('row')

            if attribute_name in default_plugin_attributes or attribute_name == '__doc__':
                if show_pyblish_attr:
                    self.attr_widgets_table.showRow(row_index)
                else:
                    self.attr_widgets_table.hideRow(row_index)

        self.pipeline_config_refresh_active_checkboxes()

    def plugin_config_show_clicked(self, *args):
        sender = self.sender()
        plugin_name = sender.text()
        self.plugin_config_show(plugin_name)

    def plugin_config_show(self, plugin_name):
        """
        handle all the fluff around showing a new plugin config widget, and create it, delete the old one
        :param plugin_name: name of the plugin
        :return: Qt widget visualising the plugin config
        """

        # get matching config
        plugin_config = self.pipeline_config[plugin_name]
        w = self.plugin_config_create_widget(plugin_config, plugin_name)

        # delete old widget
        self.hbox_main_layout.removeWidget(self.widget_plugin_config)
        self.widget_plugin_config.deleteLater()
        self.widget_plugin_config = None

        self.widget_plugin_config = w
        self.hbox_main_layout.addWidget(self.widget_plugin_config)
        w.repaint()

        self.plugin_config_color_attribute_widgets()

    def plugin_config_create_widget(self, plugin_config, plugin_name):
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

        # todo show visual difference default values vs editted, see self.color_widget
        # todo add reset to default settings button

        # create title and doc widget
        widget_plugin_config_title = QtWidgets.QLabel(plugin_name)  # "PLUGIN NAME: " +
        widget_plugin_config_title.setStyleSheet("font-size: 16px;")
        doc_string = str(plugin_config.get('__doc__', '')).strip()
        # while doc_string.startswith('\n'):
        #     doc_string = doc_string[1:]
        if doc_string == 'None':
            doc_string = ''
        self.widget_plugin_doc = QtWidgets.QLabel(doc_string)
        # layout = QtWidgets.QVBoxLayout(self)
        # self.widget_plugin_doc.setLayout(layout)
        # layout.setMargin(0)

        doc_scroll_widget = wrap_widget_in_scroll_area(self, self.widget_plugin_doc)
        doc_scroll_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        doc_scroll_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        doc_scroll_widget.setMaximumHeight(80)
        # doc_scroll_widget.SizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        # doc_scroll_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # create checkbox hide pyblish attributes
        self.hide_pyblish_attributes_widget = QtWidgets.QCheckBox("Hide Pyblish attributes")
        self.hide_pyblish_attributes_widget.stateChanged.connect(self.plugin_config_refresh_attributes)

        self.current_plugin_attributes_widgets = []  # list of attribute widgets

        self.attr_widgets_table = QtWidgets.QTableWidget()
        self.attr_widgets_table.setRowCount(len(plugin_config))
        self.attr_widgets_table.setColumnCount(3)
        self.attr_widgets_table.setHorizontalHeaderLabels(["Attribute", "Value", 'Type'])
        self.attr_widgets_table.verticalHeader().setVisible(False)
        self.attr_widgets_table.setStyleSheet("QTableWidget { "
                                                  "background-color: transparent;"
                                                  "border: 0px solid transparent;"
                                              "}"
                                              "QTableWidget::item {"
                                                  "border: 0px solid transparent;"
                                                  "padding: 0px 4px 0px 4px;}"
                                              "}"
                                              )
        i = 0
        for attribute_name, attribute_value in plugin_config.items():


            attribute_widget = self.plugin_config_create_widget_from_attribute(attribute_name, attribute_value)

            if not attribute_widget:
                continue  # skip unsupported types ex.functions, actions

            self.plugin_config_add_tooltips(attribute_widget, attribute_name)
            if attribute_name not in default_plugin_attributes:
                self.plugin_config_add_tooltips(attribute_widget, attribute_name, plugin_config['__doc__'])

            self.current_plugin_attributes_widgets.append(attribute_widget)

            lbl = QtWidgets.QLabel(attribute_name)

            # create type selector
            type_widget = QtWidgets.QComboBox()
            type_widget.addItems([x.__name__ for x in SUPPORTED_TYPES])
            print(attribute_value)
            if type(attribute_value) in SUPPORTED_TYPES:
                type_widget.setCurrentText(type(attribute_value).__name__)
                #type_widget.currentTextChanged.connect(lambda x, attribute_name=attribute_name: self.plugin_config_type_changed(x, attribute_name))

            self.attr_widgets_table.setCellWidget(i, 0, lbl)
            self.attr_widgets_table.setCellWidget(i, 1, type_widget)
            self.attr_widgets_table.setCellWidget(i, 2, attribute_widget)

            i += 1

            attribute_widget.setObjectName('attr_widget_' + attribute_name)  # not used but nice to name your widgets
            attribute_widget.setProperty('attribute_name', attribute_name)  # store the attribute name in the widget
            attribute_widget.setProperty('row', i)  # store the row in the widget

        self.attr_widgets_table.resizeColumnsToContents()
        self.attr_widgets_table.resizeRowsToContents()
        # stretch last column
        self.attr_widgets_table.horizontalHeader().setStretchLastSection(True)

        # add title, doc, and scroll widgets to main container
        plugin_config_main_layout.addWidget(widget_plugin_config_title)
        plugin_config_main_layout.addWidget(doc_scroll_widget)
        plugin_config_main_layout.addWidget(self.attr_widgets_table)
        plugin_config_main_layout.addWidget(self.hide_pyblish_attributes_widget)

        self.hide_pyblish_attributes_widget.setChecked(self.hide_pyblish_attributes)
        # self.hide_pyblish_attributes_widget.setChecked(True) # do this at the end, it triggers a refresh

        return plugin_config_main_widget

    def plugin_config_color_attribute_widgets(self):
        any_value_changed = False
        any_pyblish_default_value_changed = False  # check if any of the pyblish defult values changed, they might be hidden
        for w in self.current_plugin_attributes_widgets:
            attribute_name = w.property('attribute_name')
            value_changed = self.plugin_config_color_attribute_widget(w)
            any_value_changed = any_value_changed or value_changed

            if attribute_name in default_plugin_attributes and value_changed:
                any_pyblish_default_value_changed = True

        # if any_value_changed:
        #     pass
        self._color_widget(self.hide_pyblish_attributes_widget, any_pyblish_default_value_changed)

    def plugin_config_color_attribute_widget(self, attribute_widget):
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

    def plugin_config_create_widget_from_attribute(self, attr_name, attr_value):
        """
        Create a widget to edit the attribute.
        Add the attribute name to the widget as a property: attribute_name
        """
        # todo handle exceptions

        if attr_name.lower() == 'actions':
            return QtWidgets.QLabel(str(attr_value))  # return default widget

        widget = self.plugin_config_create_widget_from_attr_type(attr_value)



        return widget

    @staticmethod
    def plugin_config_add_tooltips(w, name, pyblish_plugin_doc=0):
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

        if 'Attributes:' in pyblish_plugin_doc:
            attribute_doc_raw = pyblish_plugin_doc.split('Attributes:')[1]
        else:
            attribute_doc_raw = pyblish_plugin_doc

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

    def plugin_config_create_widget_from_attr_type(self, value):
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
            signal_func.connect(self.plugin_config_load_values_from_widget)

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

    def plugin_config_load_values_from_widget(self):
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

        self.plugin_config_color_attribute_widgets()  # update colors when changing the widget
        self.pipeline_config_color_plugin_widgets()
        self.pipeline_config_refresh_active_checkboxes()

    # helper functions

    def _open_qfiledialog(self):
        """
        Used to browse to the save location for the config
        """
        title = "save config file"
        file_types = "Json (*.json)"
        root_folder = ""
        return QtWidgets.QFileDialog.getOpenFileName(self, title, root_folder, file_types)[0]

    @staticmethod
    def get_value_from_widget(widget):
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

    @staticmethod
    def _color_widget(widget, value_changed):
        if value_changed:
            widget.setStyleSheet("background-color: rgb(255, 200, 100);")
        else:
            widget.setStyleSheet("")

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

# todo would be cool if pipeline didnt just filter but also saved locations to paths of plugins

def make_config(discover=True, config=None, qapp=True):
    if discover:

        # get all plugins from pyblish

        # support creating a pipeline for specific hosts. ex a maya pipeline
        # todo set input before we discover. ex host maya
        # or pyblish version, see def plugins_from_module() in pyblish.plugin.py

        # api.register_host('maya')  # todo change this to not rely on maya
        # todo atm some plugins fail because of cannot import cmds from maya, when run from python

        plugins = pyblish.api.discover()
        config = get_pipeline_config_from_plugins(plugins)

    if qapp:
        app = QtWidgets.QApplication(sys.argv)

    m = manager_UI()
    m.pipeline_config_load(config)
    m.setWindowTitle('pyblish pipeline manager')
    # m.display_config(config)

    m.show()

    if qapp:
        app.exec_()


    if True:
        # app = QtWidgets.QApplication(sys.argv)

        m = QtWidgets.QWidget()
        # m.load_config(config)
        # m.setWindowTitle('pyblish pipeline manager')
        # m.display_config(config)

        layout = QtWidgets.QVBoxLayout()
        layout_buttons = QtWidgets.QHBoxLayout()
        layout_buttons.addWidget(QtWidgets.QLabel('test'))
        layout_buttons.addWidget(QtWidgets.QLabel('test'))

        path_widget = QtWidgets.QWidget()
        path_layout = QtWidgets.QVBoxLayout()
        path_widget.setLayout(path_layout)
        path_scroll_widget = wrap_widget_in_scroll_area(m, path_widget)

        layout.addLayout(layout_buttons)
        layout.addWidget(path_scroll_widget)
        m.setLayout(layout)

        pyblish.api.register_plugin_path('c:/test')
        for x in pyblish.api.registered_paths():
            layout_buttons = QtWidgets.QHBoxLayout()
            remove_path_button_widget = QtWidgets.QPushButton('-')
            remove_path_button_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            layout_buttons.addWidget(remove_path_button_widget)
            layout_buttons.addWidget(QtWidgets.QLabel(x))
            path_layout.addLayout(layout_buttons)



        m.show()
        if qapp:
            app.exec_()

    return m

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



# maya snippet
# import pyblish_config.config_creator_GUI as gui
# reload(gui)
#
# test = gui.make_config(qapp=False)
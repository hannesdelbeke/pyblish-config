import sys

import pyblish.api
from Qt import QtWidgets, QtCore, QtGui
from Qt.QtWidgets import QFileDialog

import copy

import pyblish_config.config
from pyblish_config.config import get_pipeline_config_from_plugins, PipelineConfig

try:
    from pathlib import Path
except:
    from pathlib2 import Path

SUPPORTED_TYPES = [int, float, str, bool, list, dict, tuple, type(None), ]


class plugin_widget(object):
    def __init__(self, pyblish_plugin, widget):
        # object.__init__(self)

        self.name = ""


default_plugin_attributes = dir(pyblish.plugin.Plugin)


class manager_UI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.pipeline_config = {}
        self.json_path_output = r"C:\Projects\pyblish-plugin-manager\output_config.json"  # todo remove hardcoded path
        self.json_path_input = ""
        self.hide_pyblish_attributes = True

        # create plugins list widget and layout

        # self.widgets_plugin_buttons = []
        self.widget_plugins_list = self.pipeline_config_create_plugin_list()   # the scroll list that contains the plugin buttons
        # create plugin settings widget
        # self.widget_plugin_config_container_main = self.create_right()  # sets up more self. variables inside method

        # # create placeholder
        self.widget_plugin_config = QtWidgets.QWidget(self)

        # Layout left and right widgets
        self.hbox_main_layout = QtWidgets.QHBoxLayout(self)
        # self.hbox_main_layout.addWidget(self.plugin_list_widget)
        self.hbox_main_layout.addWidget(self.widget_plugins_list)  # self.config_main_widget
        # self.hbox_main_layout.addWidget(self.widget_plugin_config_container_main)  # self.widget_plugin_config

        # self.vbox_main_layout.addWidget(self.config_buttons_widget)

        self.setLayout(self.hbox_main_layout)

        self.order_plugin_list_from_config(self.pipeline_config)

    # pipeline config

    def _del_item(self):
        for item in self.plugin_list_widget.selectedItems():
            # delete item from list
            self.plugin_list_widget.takeItem(self.plugin_list_widget.row(item))
            # delete from config
            self.pipeline_config.pop(item.text())

    def pipeline_config_create_plugin_list(self):


        self.plugin_list_widget = QtWidgets.QListWidget(self)
        self.plugin_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.plugin_list_widget.setDragEnabled(True)
        self.plugin_list_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.plugin_list_widget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.plugin_list_widget.setDropIndicatorShown(True)
        self.plugin_list_widget.setAcceptDrops(True)
        self.plugin_list_widget.setDragDropOverwriteMode(False)

        def keyPressEvent(event):
            if event.key() == QtCore.Qt.Key_Delete:
                self._del_item()



        self.plugin_list_widget.keyPressEvent = keyPressEvent
        self.plugin_list_widget._del_item = lambda: self._del_item

        # todo conenct drag and drop
        # self.plugin_list_widget.currentRowChanged.connect(self.bake_plugin_order_from_list_order)



        self.vbox_config_layout = QtWidgets.QVBoxLayout(self)  # this needs to happen before scrollarea
        # create widget, apply layout, add widgets to layout.

        # create config widget
        widget = QtWidgets.QWidget()
        widget.setLayout(self.vbox_config_layout)

        # create config buttons
        # self.register_plugins_button = QtWidgets.QPushButton('register plugins')
        self.load_config_button = QtWidgets.QPushButton('load config')
        self.save_config_button = QtWidgets.QPushButton('save config')
        self.load_config_button.clicked.connect(self.pipeline_config_browse_and_load)
        self.save_config_button.clicked.connect(self.pipeline_config_browse_and_save)

        self.discover_button = QtWidgets.QPushButton('discover (resets !!!)')
        self.discover_button.clicked.connect(self.discover)
        # self.discover_button.setMaximumWidth(50)

        self.config_button_layout = QtWidgets.QHBoxLayout()
        # self.config_button_layout.addWidget(self.register_plugins_button)
        self.config_button_layout.addWidget(self.load_config_button)
        self.config_button_layout.addWidget(self.save_config_button)

        # dropdown = QtWidgets.QComboBox()
        # dropdown.addItems(['register plugins', 'configure pipeline'])


        label = QtWidgets.QLabel('pipeline:')
        # self.vbox_config_layout.addWidget(dropdown)
        # self.vbox_config_layout.addWidget(widget_scroll)
        # text fill box
        self.config_name_widget = QtWidgets.QTextEdit()
        self.config_name_widget.setFixedHeight(20)
        self.config_name_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.config_name_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.config_name_widget)

        self.vbox_config_layout.addWidget(self.discover_button)
        self.vbox_config_layout.addWidget(self.plugin_list_widget)
        self.vbox_config_layout.addLayout(layout)
        self.vbox_config_layout.addLayout(self.config_button_layout)

        return widget

    def discover(self):
        plugins = pyblish.api.discover()
        config = get_pipeline_config_from_plugins(plugins)
        for x in config:
            for y in x:
                print(x, y)
        self.pipeline_config_load(config)


    def pipeline_config_plugin_buttons_create_widget(self):

        self.plugin_list_widget.addItems(self.pipeline_config.keys())
        self.plugin_list_widget.itemClicked.connect(self.plugin_config_show_clicked)

    def pipeline_config_browse_and_save(self):
        """
        save UI settings into a json settings file
        """

        # get path
        browsed_path = self._save_qfiledialog().replace("/", "\\")
        if browsed_path:
            self.json_path_output = browsed_path

        # todo fix that
        #  naively assume differences can be calc between configs
        #  this wont work if we edit an already different config
        # this diff is only needed when doing register_plugin -> discover -> plugins ->config
        # when we edit an alrdy existing config we dont need to do any diffing
        config_data = pyblish_config.config.diff_pipeline_configs(self.pipeline_config, self.original_pipeline_config)

        # config_data = PipelineConfig(self.pipeline_config)
        # config_data.filter_default_attributes()

        # TODO make this compatible with collect, validate, extract, integrate phases.
        #  right now bake order breaks this resulting in issues in QML etc
        # self.bake_plugin_order_from_list_order()

        # config_data = self.pipeline_config

        config_data.dump(self.json_path_output)

        name = Path(self.json_path_output).stem
        self.config_name_widget.setText(name)

    def bake_plugin_order_from_list_order(self, *args):
        """mutate input config_data to bake plugin order from list order"""
        items = [self.plugin_list_widget.item(x) for x in range(self.plugin_list_widget.count())]
        i = 0
        for item in items:
            plugin_name = item.text()
            self.pipeline_config[plugin_name]['order'] = i
            i += 1
        self.plugin_config_color_attribute_widgets()

    def order_plugin_list_from_config(self, config_data):
        # get the order from the config_data
        order_dict = {plugin_name: config_data[plugin_name]['order'] for plugin_name in config_data.keys()}
        # get items from list widget
        items = [self.plugin_list_widget.item(x) for x in range(self.plugin_list_widget.count())]
        # sort items by order
        items_sorted = sorted(items, key=lambda x: order_dict[x.text()])
        # remove all items from list widget
        for item in items:
            self.plugin_list_widget.takeItem(self.plugin_list_widget.row(item))
        # add items back to list widget
        for item in items_sorted:
            self.plugin_list_widget.addItem(item)


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
        config = pyblish_config.config.load_config_from_json(browsed_path)  # todo verify the loaded config is valid
        # run discover again?

        # ## additive loading of config
        # loaded_config = pyblish_config.config.load_config_from_json(browsed_path)
        # for plugin_name, plugin_config in loaded_config.items():
        #     for attr_name, value in plugin_config.items():
        #         self.pipeline_config.setdefault(plugin_name, {})
        #         self.pipeline_config[plugin_name][attr_name] = value

        self.pipeline_config_load(config)

        filename = Path(browsed_path).stem
        self.config_name_widget.setText(filename)

        # refresh colors
        # self.plugin_config_color_attribute_widgets()
        # self.pipeline_config_color_plugin_widgets()

        # todo handle case where the discover does not contain plugin but the config does, same with attributes
        # ex discover returns plugin 1 and 2, but config also contains settings for plugin 3
        # might not be returned because it has a compile error since a recent update

    def pipeline_config_refresh(self):
        self.plugin_list_widget.clear()
        self.pipeline_config_plugin_buttons_create_widget()
        self.order_plugin_list_from_config(self.pipeline_config)

    def pipeline_config_load(self, pipeline_config):
        self.original_pipeline_config = copy.deepcopy(pipeline_config)
        self.pipeline_config = copy.deepcopy(pipeline_config)

        # plugin screen
        self.pipeline_config_refresh()

        # config screen
        self.plugin_config_show_first()

    def pipeline_config_color_plugin_widgets(self):
        items = [self.plugin_list_widget.item(x) for x in range(self.plugin_list_widget.count())]

        for item in items:

            # check if value changed
            value_changed = False

            plugin_name = item.text()
            original_config = self.original_pipeline_config[plugin_name]
            current_config = self.pipeline_config[plugin_name]

            for key, value in current_config.items():
                if original_config[key] != value:
                    value_changed = True
                    break

            if value_changed:
                # set color yellow
                color = QtGui.QColor(255, 200, 100, 100)
            else:
                # set color transparent
                color = QtGui.QColor(255, 255, 255, 0)
            item.setBackground(color)


    def plugin_config_show_first(self):
        # get first item text
        plugin_name = self.plugin_list_widget.item(0).text()
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

    def plugin_config_show_clicked(self, *args):
        sender = self.sender()
        plugin_name = sender.selectedItems()[0].text()
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
        :param plugin_config:
        :param plugin_name:
        :return: the plugin config widget
        """
        self.current_plugin_name = plugin_name

        # create main container
        plugin_config_main_widget = QtWidgets.QWidget()
        plugin_config_main_layout = QtWidgets.QVBoxLayout(self)
        plugin_config_main_widget.setLayout(plugin_config_main_layout)

        # todo add reset to default settings button

        # create title and doc widget
        widget_plugin_config_title = QtWidgets.QLabel(plugin_name)  # "PLUGIN NAME: " +
        widget_plugin_config_title.setStyleSheet("font-size: 16px;")
        doc_string = str(plugin_config.get('__doc__', '')).strip()
        # while doc_string.startswith('\n'):
        #     doc_string = doc_string[1:]
        if doc_string == 'None':
            doc_string = ''

        # create scrollable text widget
        doc_widget = QtWidgets.QTextEdit()
        doc_widget.setReadOnly(True)
        doc_widget.setText(doc_string)
        doc_widget.setStyleSheet("font-size: 11px;")
        doc_widget.setFixedHeight(100)
        # set overflow to flase to allow scrolling
        # add horizon scroll to true
        doc_widget.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        doc_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        doc_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # self.widget_plugin_doc = QtWidgets.QLabel(doc_string)

        # doc_scroll_widget = wrap_widget_in_scroll_area(self, self.widget_plugin_doc)
        # doc_scroll_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # doc_scroll_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # doc_scroll_widget.setMaximumHeight(80)

        # create checkbox hide pyblish attributes
        self.hide_pyblish_attributes_widget = QtWidgets.QCheckBox("Hide Pyblish attributes")
        self.hide_pyblish_attributes_widget.stateChanged.connect(self.plugin_config_refresh_attributes)

        self.current_plugin_attributes_widgets = []  # list of attribute widgets

        self.attr_widgets_table = QtWidgets.QTableWidget()
        self.attr_widgets_table.setRowCount(len(plugin_config))
        self.attr_widgets_table.setColumnCount(2)
        self.attr_widgets_table.setHorizontalHeaderLabels(["Attribute", "Value"])
        self.attr_widgets_table.verticalHeader().setVisible(False)
        self.attr_widgets_table.setStyleSheet("QTableWidget { "
                                                  "background-color: transparent;"
                                                  "border: 0px solid transparent;"
                                              "}"
                                              "QTableWidget::item {"
                                                  "border: 0px solid transparent;"
                                              #    "padding: 0px 4px 0px 4px;}"
                                              "}"
                                              "QLabel {padding: 0px 4px 0px 4px;}"
                                              "QCheckBox {padding: 0px 4px 0px 4px;}"
                                              )

        # store list of types for default
        # iterables by default contain comma seperated strings
        default_plugin_attribute_types = {
            'actions': [],
            'active': bool,
            'families': [],
            'hosts': [],
            'label': str,
            'match': int,
            'optional': bool,
            'order': float,
            'requires': str,
            'targets': [],
            'version': tuple,
            '__doc__': str,
        }

        i = 0
        for attribute_name, attribute_value in plugin_config.items():
            attribute_type = default_plugin_attribute_types.get(attribute_name, None)
            attribute_widget = self.plugin_config_create_widget_from_attribute(attribute_name, attribute_value, attribute_type)

            if not attribute_widget:
                attribute_widget = QtWidgets.QLabel(str(attribute_value))
                # continue  # skip unsupported types ex.functions, actions

            self.plugin_config_add_tooltips(attribute_widget, attribute_name)
            if attribute_name not in default_plugin_attributes:
                self.plugin_config_add_tooltips(attribute_widget, attribute_name, plugin_config.get('__doc__', ''))

            self.current_plugin_attributes_widgets.append(attribute_widget)

            lbl = QtWidgets.QLabel(attribute_name)

            # type
            # if attribute_name not in default_plugin_attributes:
            #     # create type selector
            #     type_widget = QtWidgets.QComboBox()
            #     type_widget.addItems([x.__name__ for x in SUPPORTED_TYPES])
            #     if type(attribute_value) in SUPPORTED_TYPES:
            #         type_widget.setCurrentText(type(attribute_value).__name__)
            #         #type_widget.currentTextChanged.connect(lambda x, attribute_name=attribute_name: self.plugin_config_type_changed(x, attribute_name))
            #     self.attr_widgets_table.setCellWidget(i, 2, type_widget)

            self.attr_widgets_table.setCellWidget(i, 0, lbl)
            self.attr_widgets_table.setCellWidget(i, 1, attribute_widget)

            attribute_widget.setObjectName('attr_widget_' + attribute_name)  # not used but nice to name your widgets
            attribute_widget.setProperty('attribute_name', attribute_name)  # store the attribute name in the widget
            attribute_widget.setProperty('row', i)  # store the row in the widget

            i += 1

        self.attr_widgets_table.resizeColumnsToContents()
        self.attr_widgets_table.resizeRowsToContents()
        self.attr_widgets_table.horizontalHeader().setStretchLastSection(True)

        # add title, doc, and scroll widgets to main container
        plugin_config_main_layout.addWidget(widget_plugin_config_title)
        plugin_config_main_layout.addWidget(doc_widget)
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

    def plugin_config_create_widget_from_attribute(self, attr_name, attr_value, attr_type=None):
        """
        Create a widget to edit the attribute.
        Add the attribute name to the widget as a property: attribute_name
        """
        # todo handle exceptions

        if attr_name.lower() == 'actions':
            return QtWidgets.QLabel(str(attr_value))  # return default widget

        widget = self.plugin_config_create_widget_from_attr_type(attr_value, attr_type)

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

    def plugin_config_create_widget_from_attr_type(self, value, attr_type=None):
        """
        decide which widget to use based on the attribute type
        :param attr:
        :param value:
        :return:
        """
        w = None
        signal_func = None  # state to connect too
        if not attr_type:
            if isinstance(value, str):
                attr_type = str
            elif isinstance(value, list) or attr_type is tuple:
                attr_type = list
            else:
                attr_type = type(value)

        if attr_type is bool:
            w = QtWidgets.QCheckBox()
            w.setChecked(value)
            signal_func = w.stateChanged

        elif attr_type is int:
            w = QtWidgets.QSpinBox()
            w.setValue(value)
            signal_func = w.valueChanged

        elif attr_type is float:
            w = QtWidgets.QDoubleSpinBox()
            w.setValue(value)
            signal_func = w.valueChanged

        elif attr_type is str:
            w = QtWidgets.QLineEdit(value)
            signal_func = w.textChanged

        elif attr_type is list:
            # list to comma separated string
            value_str = ''

            for x in value:
                if len(value_str) > 0:
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
        # self.pipeline_config_refresh_active_checkboxes()

    # helper functions

    # def _open_qfiledialog(self):
    #     """
    #     Used to browse to the load location for the config
    #     """
    #     title = "save config file"
    #     file_types = "Json (*.json)"
    #     root_folder = ""
    #     return QtWidgets.QFileDialog.getOpenFileName(self, title, root_folder, file_types)[0]

    def _save_qfiledialog(self):
        """
        Used to browse to the save location for the config
        """
        title = "save config file"
        file_types = "Json (*.json)"
        default_name = self.config_name_widget.toPlainText()
        return QtWidgets.QFileDialog.getSaveFileName(self, title, default_name, file_types)[0]

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
        if value_type is list:  # add tuple support
            value = text.split(',')
            if not text:
                value = []

        return value

    @staticmethod
    def _color_widget(widget, value_changed):
        if value_changed:
            widget.setStyleSheet("background-color: rgb(255, 200, 100, 100);")
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

    app = QtWidgets.QApplication.instance()
    new_app = False
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        new_app = True

    m = manager_UI()
    m.pipeline_config_load(config)
    m.setWindowTitle('pyblish pipeline manager')
    # m.display_config(config)

    m.show()

    if new_app:
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
# test = gui.make_config()
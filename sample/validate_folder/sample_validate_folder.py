import pyblish.api

# register GUI
pyblish.api.register_gui("pyblish_qml")
pyblish.api.register_gui("pyblish_lite")

# from pyblish_qml import api, show
# # Tell QML about dependencies
# api.register_python_executable("C:/Python27/python.exe")
# api.register_pyqt5("C:/modules/python-qt5")

# unregister the default plugins
pyblish.api.deregister_all_plugins()
pyblish.api.deregister_all_paths()

# register my plugin
from sample.validate_folder.CollectFilePaths import CollectFilePaths
pyblish.api.register_plugin(CollectFilePaths)

from sample.validate_folder.ValidateFilePaths import ValidateFilePaths
pyblish.api.register_plugin(ValidateFilePaths)

import pyblish_lite
pyblish_lite.show()

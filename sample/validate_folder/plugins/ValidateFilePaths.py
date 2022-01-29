import pyblish.api
import pathlib2 as pathlib

class ValidateFilePaths(pyblish.api.InstancePlugin):
    """
    Check all paths follow the correct format
    Attributes:
        pattern_name (str): The pattern to be used.
    """
    label = "check FileNames starts with"
    order = pyblish.api.ValidatorOrder
    families = ['paths']

    pattern_name = 'FF_*.ma'

    def process(self, instance):
        assert pathlib.Path(instance.name).match(self.pattern_name)


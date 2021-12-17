import pyblish.api
import pathlib2 as pathlib

class ValidateFilePaths(pyblish.api.InstancePlugin):
    label = "check FileNames starts with"
    order = pyblish.api.ValidatorOrder
    families = ['paths']

    pattern_name = 'FF_*.ma'

    def process(self, instance):
        assert pathlib.Path(instance.name).match(self.pattern_name)


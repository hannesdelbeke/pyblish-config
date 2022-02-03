import pyblish.api
import pyblish.plugin
import pyblish.util

# register convertor
from pyblish_extended.convertor.plugins.convertor_string_int import ConverterStringInt

# collect string
class collectString(pyblish.api.ContextPlugin):
    order = pyblish.api.CollectorOrder

    def process(self, context):
        inst = context.create_instance("mesh names", icon="cubes", families=['string'])
        inst[:] = ["5", "6", "8"]
        inst = context.create_instance("mesh names fail", icon="cubes", families=['string'])
        inst[:] = ["5", "6", "test"]


# run validation test to check if int
class validateInt(pyblish.api.Validator):
    families = ['int']
    order = pyblish.api.ValidatorOrder

    def process(self, instance, context):
        print(self.families, instance)
        for data in instance:
            print(data)
            assert isinstance(data, int)


pyblish.api.register_plugin(ConverterStringInt)
pyblish.api.register_plugin(collectString)
pyblish.api.register_plugin(validateInt)

pyblish.util.publish()


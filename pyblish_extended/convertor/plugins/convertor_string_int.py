from pyblish_extended.convertor.convertor_pymesh_meshname import ConvertorInstance
import pyblish.api

class ConverterStringInt(pyblish.api.ContextPlugin):
    """
    create a converter instance
    """
    order = pyblish.api.CollectorOrder
    families = ['string']  # the input family, instances will find the convertor from this family

    # options
    output_family = 'int'

    @staticmethod
    def string_to_int(instances):
        for instance in instances:
            for string in instance:
                yield int(string)

    def process(self, context):
        ConvertorInstance(converter_function=self.string_to_int,
                          name="Converter string to int",
                          family=self.output_family,
                          input_families=self.families,
                          parent=context)

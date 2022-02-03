# register a convertor for pymesh meshname

import pyblish.api
import pyblish.plugin
import pathlib2 as pathlib


class ConvertorInstance(pyblish.plugin.Instance):

    def __init__(self, converter_function, input_families, *args, **kwargs):
        """
        input_families: the family to find instances that need converting
        ex. pymesh

        family/families: the family used by validators to find the converted instances
        ex. meshname

        :param converter_function: function to convert the instance, can be a generator or anything iterable.
        """
        self.converter_function = converter_function
        self.input_families = input_families
        super(ConvertorInstance, self).__init__(*args, **kwargs)

    def __iter__(self):
        context = self._parent  # does not yet support instances parented to other instances, only parented to context
        mock_plugin = pyblish.api.Plugin
        mock_plugin.families = self.input_families
        original_instances = pyblish.logic.instances_by_plugin(context, mock_plugin)

        self.converted_instances = self.converter_function(original_instances)

        for instance in self.converted_instances:
            yield instance


class ConverterPymeshMeshname(pyblish.api.ContextPlugin):
    """
    create a converter instance
    """
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    families = ['pymesh']  # the input family, instances will find the convertor from this family

    # options
    output_family = 'meshname'

    @staticmethod
    def pymesh_to_meshname(instances):
        for mesh in instances:
            yield mesh.name

    def process(self, context):
        ConvertorInstance(converter_function=self.pymesh_to_meshname,
                          name="Converter Pymesh Meshname",
                          family=self.output_family,
                          input_families=self.families,
                          parent=context)

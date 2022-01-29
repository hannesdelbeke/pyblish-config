import pyblish.api
import pathlib2 as pathlib


class Options(object):
    pass

class CollectFilePaths(pyblish.api.ContextPlugin):
    """
    Collect all file paths in a folder as pyblish instances.

    Attributes:
        combine_paths (bool): Combine all paths into one Pyblish instance if True.
                Or create a separate instance for each path.
        folder_path (str): Path to the folder containing the files.
    """
    label = "Collect FileNames as Path"
    order = pyblish.api.CollectorOrder
    # hosts = ["maya"]
    families = ['paths']

    # options = Options()
    # options.folder_path = r'C:\Projects\pyblish-plugin-manager\sample\test files\projects\final fantasia FANTASY RPG\meshes'
    # options.combine_paths = False

    folder_path = r'C:\Projects\pyblish-plugin-manager\sample\test files\projects\final fantasia FANTASY RPG\meshes'
    combine_paths = False

    def process(self, context):
        paths = pathlib.Path(self.folder_path)
        if self.combine_paths:
            instance_controls = context.create_instance("FilePaths", family='paths')
            instance_controls[:] = paths.iterdir()
        else:
            for path in paths.iterdir():
                instance_controls = context.create_instance(str(path.name), family='paths')
                instance_controls[:] = [path]
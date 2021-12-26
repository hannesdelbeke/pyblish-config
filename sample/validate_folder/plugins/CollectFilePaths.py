import pyblish.api
import pathlib2 as pathlib

class CollectFilePaths(pyblish.api.ContextPlugin):
    """
    Collect all file paths in a folder.
    Set the folder path in mesh_folder_path.
    If comine_paths is True, all paths will be stored in one Pyblish instance,
    otherwise you get a separate instance for each path found.
    """
    label = "Collect FileNames as Path"
    order = pyblish.api.CollectorOrder
    # hosts = ["maya"]
    families = ['paths']

    mesh_folder_path = r'C:\Projects\pyblish-plugin-manager\sample\test files\projects\final fantasia FANTASY RPG\meshes'
    combine_paths = False

    def process(self, context):
        paths = pathlib.Path(self.mesh_folder_path)
        if self.combine_paths:
            instance_controls = context.create_instance("FilePaths", family='paths')
            instance_controls[:] = paths.iterdir()
        else:
            for path in paths.iterdir():
                instance_controls = context.create_instance(str(path.name), family='paths')
                instance_controls[:] = [path]
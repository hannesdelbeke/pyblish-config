import pymel.core as pm

class CollectMeshes(pyblish.api.ContextPlugin):
    label = "Collect Meshes"
    order = pyblish.api.CollectorOrder
    hosts = ["maya"]
    families = ['meshes']

    def process(self, context):
	meshes = pm.ls(type = 'mesh')
        instance_controls = context.create_instance("Meshes", icon="cubes", family='meshes')
        instance_controls[:] = meshes 
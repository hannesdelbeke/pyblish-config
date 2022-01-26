import sample.validate_folder.sample_validate_folder_FF

# we steal the setup from our other project, FF
# instead of inheriting the plugins and overwritting settings,
# and then reregistering the plugins here.
# we use the pipeline to overwrite settings for the registered plugins

# pipeline
from pyblish_config.config import register_pipeline_config_filter
register_pipeline_config_filter('sample_config_folder.json')

import pyblish_lite
pyblish_lite.show()
from pyblish_config import config

# load config, filter out attributes, save back
config_path = r'C:\my_config.json'
c = config.load_config_from_json(config_path)
c = config.filter_attrs(c, attributes=['url'])
c = config.filter_empty_plugins(c)
config.save_config_as_json(path=config_path, config_data=c)

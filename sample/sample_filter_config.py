from pyblish_config import config

# load config, filter out attributes, save back
config_path = r'C:\my_config.json'
c = config.load_config_from_json(config_path)
config.filter_attrs(attributes=['url'])
config.filter_empty_plugins()
config.dump(path=config_path)

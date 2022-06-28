from pyblish_config.config import load_config_from_json

# load config, filter out attributes, save back
config_path = r'C:\my_config.json'
config = load_config_from_json(config_path)
config.filter_attrs(attributes=['url'])
config.filter_empty_plugins()
config.dump(path=config_path)

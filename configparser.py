import json
from os import path

class ConfigParser():
  def __init__(self, config_filename):
    self.filename = config_filename

  def arg_check(self, config):
    """
      Add check for config file here.
      Return None if given config is not sufficient
    """
    print(config)
    return config

  def parse(self):
    try:
      if not path.isfile(self.filename):
        print('File does not exist')
        return None
      with open(self.filename) as f:
        config = json.load(f)
        return self.arg_check(config)
    except ValueError as e:
      print('invalid json: %s' % e)
      return None

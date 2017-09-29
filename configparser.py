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
    if 'build' not in config or 'job' not in config:
      print('Need build and job in json file')
      return None
    if self.config_build_check(config['build']) and self.config_job_check(config['job']):
      print(config)
      return config
    return None

  def config_build_check(self, build):
    """
      Add check for build parameters here
      Return False if something is missing.
    """
    return True

  def config_job_check(self, job):
    """
      Add check for job parameters here.
      Return False if something is missing.
    """
    return True

  def parse(self):
    try:
      if not path.isfile(self.filename):
        print('File does not exist')
        return None
      with open(self.filename) as f:
        config = json.load(f)
        print(config)
        return self.arg_check(config)
    except ValueError as e:
      print('invalid json: %s' % e)
      return None

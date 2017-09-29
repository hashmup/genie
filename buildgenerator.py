from generator import Generator
from fileutil import *

class BuildGenerator(Generator):
  def __init__(self, params):
    Generator.__init__(self, [['build', 'sh'], ['build_config', 'sh']])
    self.params = params
  def gen(self):
    tmp = self.contents["build"]['template'].render(neuron_path=self.params["build"]["neuron_path"], config_path=self.contents["build_config"]['output_file'], specials_path=self.params["build"]["specials_path"])
    write_file(self.contents["build"]['output_file'], tmp)
    tmp = self.contents["build_config"]['template'].render(options=self.params["build_config"]["options"], compile_options=self.params["build_config"]["compile_options"])
    write_file(self.contents["build_config"]['output_file'], tmp)

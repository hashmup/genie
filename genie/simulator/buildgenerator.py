from generator import Generator
from utils.fileutil import *


class BuildGenerator(Generator):
    def __init__(self):
        Generator.__init__(self, [['build', 'sh'], ['build_config', 'sh']])

    def gen(self, build_params):
        tmp = self.contents["build"]['template'].render(
            neuron_path=build_params["neuron_path"],
            config_path=self.contents["build_config"]['output_file'],
            specials_path=build_params["specials_path"]
        )
        write_file(self.contents["build"]['output_file'], tmp)
        tmp = self.contents["build_config"]['template'].render(
            options=build_params["options"],
            compile_options=build_params["compile_options"]
        )
        write_file(self.contents["build_config"]['output_file'], tmp)

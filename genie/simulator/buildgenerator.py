from simulator.generator import Generator
from utils.fileutil import *


class BuildGenerator(Generator):
    def __init__(self):
        Generator.__init__(self, [['build', 'sh'], ['build_config', 'sh']])

    def gen(self, build_params, use_tmp, env):
        neuron_path = build_params["neuron_path"]
        specials_path = build_params["specials_path"]
        if use_tmp:
            neuron_path += ".tmp"
            specials_path += ".tmp"
        if env == "cluster":
            env = "x86_64"
        elif env == "k":
            env = "sparc64"
        tmp = self.contents["build"]['template'].render(
            neuron_path=neuron_path,
            config_path=self.contents["build_config"]['output_file'],
            specials_path=specials_path,
            env=env
        )
        write_file(self.contents["build"]['output_file'], tmp)
        tmp = self.contents["build_config"]['template'].render(
            options=build_params["options"],
            compile_options=build_params["compile_options"]
        )
        write_file(self.contents["build_config"]['output_file'], tmp)

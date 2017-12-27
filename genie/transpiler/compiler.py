import os
from .neuron.neuron_func import NeuronFunc
from .neuron.ode import ODE
from .neuron.reg import Reg
from .neuron.user_func import UserFunc
from .neuron.variable import Variable
from .parser.lems import LemsCompTypeGenerator
from .fileutil import *
from os.path import join, dirname, abspath
from jinja2 import Environment, FileSystemLoader


ROOT = abspath(dirname(__file__))


class Compiler():
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'neuron/template'))
        )
        self.jinja_template = self.jinja_env.get_template(
            "base.c"
        )
        self.lems_comp_type_generator = LemsCompTypeGenerator()
        self.neuron_func = NeuronFunc()
        self.ode = ODE()
        self.reg = Reg()
        self.user_func = UserFunc()
        self.variable = Variable()

    def parse(self, path):
        with open(path, "r") as f:
            data = f.read()
        self.lems_comp_type_generator.compile_to_string(data)
        return self.lems_comp_type_generator.root

    def compile(self, path):
        root = self.parse(path)
        filename = self.get_filename(path)
        return self.jinja_template.render(
            global_variable=self.variable.compile(filename, root),
            reg=self.reg.compile(filename, root),
            user_func=self.user_func.compile(filename, root),
            ode_func=self.ode.compile(filename, root),
            neuron_func=self.neuron_func.compile(filename, root)
        )

    def gen(self, path):
        self.setup_dir()
        write_file(self.get_output_filepath(path), self.compile(path))

    def get_filename(self, path):
        base = os.path.basename(path)
        return os.path.splitext(base)[0]

    def get_output_filepath(self, path):
        return os.path.join(
            join(ROOT, 'tmp'), "{0}.c".format(self.get_filename(path))
        )

    def setup_dir(self):
        mkdir(join(ROOT, 'tmp'))

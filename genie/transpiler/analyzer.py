import os
from transpiler.neuron.neuron_func import NeuronFunc
from transpiler.neuron.ode import ODE
from transpiler.neuron.reg import Reg
from transpiler.neuron.user_func import UserFunc
from transpiler.neuron.variable import Variable
from transpiler.parser.lems import LemsCompTypeGenerator
from utils.fileutil import *
from os.path import join, dirname, abspath
from jinja2 import Environment, FileSystemLoader


ROOT = abspath(dirname(__file__))


class Analyzer():
    def __init__(self):
        self.lems_comp_type_generator = LemsCompTypeGenerator()
        self.neuron_func = NeuronFunc()
        self.ode = ODE()
        self.reg = Reg()
        self.user_func = UserFunc()
        self.variable = Variable()

    def parse(self):
        with open(self.path, "r") as f:
            data = f.read()
        self.lems_comp_type_generator.compile_to_string(data)
        return self.lems_comp_type_generator.root

    def gen(self, path):
        self.path = path
        self.setup_dir()
        write_file(
            self.get_output_filepath(),
            self.compile())

    def get_symbols(self, path):
        self.path = path
        return self.parse()

    def get_filename(self):
        base = os.path.basename(self.path)
        return os.path.splitext(base)[0]

    def get_output_filepath(self):
        return os.path.join(
            join(ROOT, 'tmp'), "{0}.c".format(self.get_filename())
        )

    def setup_dir(self):
        mkdir(join(ROOT, 'tmp'))

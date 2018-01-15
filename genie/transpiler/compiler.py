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

    def parse(self):
        with open(self.path, "r") as f:
            data = f.read()
        self.lems_comp_type_generator.compile_to_string(data)
        return self.lems_comp_type_generator.root

    def compile(self, table_order):
        root = self.parse()
        filename = self.get_filename()
        return self.jinja_template.render(
            global_variable=self.variable.compile(filename, root, table_order),
            reg=self.reg.compile(filename, root, table_order),
            user_func=self.user_func.compile(filename, root, table_order),
            ode_func=self.ode.compile(filename, root, table_order),
            neuron_func=self.neuron_func.compile(filename, root, table_order)
        )

    def gen(self, path, table_order):
        self.path = path
        self.setup_dir()
        write_file(
            self.get_output_filepath(),
            self.compile(table_order))

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

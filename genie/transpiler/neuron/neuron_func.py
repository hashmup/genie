from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from transpiler.neuron.nrn.nrn_alloc import NrnAlloc
from transpiler.neuron.nrn.nrn_cur import NrnCur
from transpiler.neuron.nrn.nrn_init import NrnInit
from transpiler.neuron.nrn.nrn_state import NrnState


ROOT = abspath(dirname(__file__))


class NeuronFunc():
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'template'))
        )
        self.jinja_template = self.jinja_env.get_template(
            "neuron_func.c"
        )
        self.nrn_alloc = NrnAlloc()
        self.nrn_cur = NrnCur()
        self.nrn_init = NrnInit()
        self.nrn_state = NrnState()

    def gen(self, root, macro_table):
        return {
            "nrn_alloc": self.nrn_alloc.gen(root),
            "nrn_cur": self.nrn_cur.gen(root, macro_table),
            "nrn_init": self.nrn_init.gen(root, macro_table),
            "nrn_state": self.nrn_state.gen(root, macro_table)
        }

    def compile(self, filename, root, macro_table):
        tokens = self.gen(root, macro_table)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

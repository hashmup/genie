from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from .nrn.nrn_alloc import NrnAlloc
from .nrn.nrn_cur import NrnCur
from .nrn.nrn_init import NrnInit
from .nrn.nrn_state import NrnState


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

    def gen(self, root):
        return {
            "nrn_alloc": self.nrn_alloc.gen(root),
            "nrn_cur": self.nrn_cur.gen(root),
            "nrn_init": self.nrn_init.gen(root),
            "nrn_state": self.nrn_state.gen(root)
        }

    def compile(self, filename, root):
        tokens = self.gen(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

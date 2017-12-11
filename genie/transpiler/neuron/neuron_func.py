from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from .nrn.nrn_alloc import NrnAlloc


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

    def parse(self, root):
        return {
            "nrn_alloc": self.nrn_alloc.gen(root)
        }

    def compile(self, filename, root):
        tokens = self.parse(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

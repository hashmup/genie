from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath


ROOT = abspath(dirname(__file__))


class Reg():
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'template'))
        )
        self.jinja_template = self.jinja_env.get_template(
            "reg.c"
        )

    def parse(self, root):
        return {}

    def compile(self, filename, root):
        tokens = self.parse(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

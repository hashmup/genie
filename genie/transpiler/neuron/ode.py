from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from textx.model import children_of_type, parent_of_type


ROOT = abspath(dirname(__file__))


class ODE():
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'template'))
        )
        self.jinja_template = self.jinja_env.get_template(
            "ode_func.c"
        )

    def gen(self, root):
        return {
            "num_states": self.get_num_states(root),
            "read_ions": self.get_read_ions(root),
            "ode_spec1": self.get_ode_spec1(root),
            "ode_matsol1": self.get_ode_matsol1(root)
        }

    def get_num_states(self, root):
        return "{0}".format(len(children_of_type('State', root)[0].state_vars))

    def get_read_ions(self, root):
        code = ""
        for x in children_of_type('UseIon', root):
            code += "\t\t{0} = _ion_{0};\n"\
                    .format(x.r[0].reads[0].name)
        return code

    def get_ode_spec1(self, root):
        code = ""
        for state in children_of_type('State', root)[0].state_vars:
            code += "\tD{0} = ({0}inf - {0}) / {0}tau;\n"\
                    .format(state.name)
        return code

    def get_ode_matsol1(self, root):
        code = ""
        for state in children_of_type('State', root)[0].state_vars:
            code += "\tD{0} = D{0} / (1. + dt / {0}tau);\n"\
                    .format(state.name)
        return code

    def compile(self, filename, root, table_order):
        tokens = self.gen(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

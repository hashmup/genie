from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from textx.model import children_of_type, parent_of_type


ROOT = abspath(dirname(__file__))


class UserFunc():
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'template'))
        )
        self.jinja_template = self.jinja_env.get_template(
            "user_func.c"
        )

    def gen(self, root):
        return {
            "check_rates": self.get_check_rates(root),
            "n_rates_lt_0": self.get_n_rates_lt_0(root),
            "n_rates_gt_200": self.get_n_rates_gt_200(root),
            "n_rates_global": self.get_n_rates_global(root),
            "f_rates": self.get_f_rates(root)
        }

    def get_check_rates(self, root):
        code = ""
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\t\t_t_{0}[_i] = {0};\n"\
                    .format(param.name)
        return code

    def get_n_rates_lt_0(self, root):
        code = ""
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\t{0} = _t_{0}[0];\n"\
                    .format(param.name)
        return code

    def get_n_rates_gt_200(self, root):
        code = ""
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\t\t{0} = _t_{0}[200];\n"\
                    .format(param.name)
        return code

    def get_n_rates_global(self, root):
        code = ""
        for param in children_of_type('Global', root)[0].globals:
            code +=\
                "\t{0} = _t_{0}[_i] + _theta * (_t_{0}[_i+1] - _t_{0}[_i]);\n"\
                .format(param.name)
        return code

    def get_f_rates(self, root):
        return ""

    def compile(self, filename, root):
        tokens = self.gen(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

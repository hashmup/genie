from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from textx.model import children_of_type, parent_of_type


ROOT = abspath(dirname(__file__))


class Reg():
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'template'))
        )
        self.jinja_template = self.jinja_env.get_template(
            "reg.c"
        )

    def gen(self, root):
        return {
            "ion_reg": self.get_ion_reg(root),
            "ion_symbol": self.get_ion_symbol(root),
            "hoc_dparam_size": self.get_hoc_dparam_size(root),
            "help": self.get_help(root),
            "initlists": self.get_initlists(root),
            "nrn_update_ion_pointer": self.get_nrn_update_ion_pointer(root)
        }

    def get_ion_reg(self, root):
        code = ""
        for ion in children_of_type('UseIon', root):
            code += "\tion_reg(\"{0}\", -10000.);\n".format(ion.ion)
        return code

    def get_ion_symbol(self, root):
        code = ""
        for ion in children_of_type('UseIon', root):
            code += "\t_{0}_sym = hoc_lookup(\"{0}_ion\");\n".format(ion.ion)
        return code

    def get_help(self, root):
        code = ""

    def get_hoc_dparam_size(self, root):
        ions = children_of_type('UseIon', root)
        return "{0}".format(len(ions) * 3 + 1)

    def get_nrn_update_ion_pointer(self, root):
        code = ""
        cnt = 0
        for ion in children_of_type('UseIon', root):
            code += "\tnrn_update_ion_pointer(_{0}_sym, _ppvar, {1}, 0);\n"\
                    "\tnrn_update_ion_pointer(_{0}_sym, _ppvar, {2}, 3);\n"\
                    "\tnrn_update_ion_pointer(_{0}_sym, _ppvar, {3}, 4);\n"\
                    .format(ion.ion,
                            cnt * 3,
                            cnt * 3 + 1,
                            cnt * 3 + 2)
            cnt += 1
        return code

    def get_initlists(self, root):
        code = ""
        cnt = 0
        for state in children_of_type('State', root)[0].state_vars:
            code += "\t_slist1[{0}] = &({1}) - _p;\n"\
                    "\t_dlist1[{0}] = &(D{1}) - _p;\n"\
                    .format(cnt, state.name)
            cnt += 1
        for param in children_of_type('Global', root)[0].globals:
            code += "\t_t_{0} = makevector(201 * sizeof(double));\n"\
                    .format(param.name)
        return code

    def compile(self, filename, root, table_order):
        tokens = self.gen(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

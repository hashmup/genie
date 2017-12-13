from functools import reduce
from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from textx.model import children_of_type, parent_of_type


ROOT = abspath(dirname(__file__))


class Variable():
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'template'))
        )
        self.jinja_template = self.jinja_env.get_template(
            "global_variable.c"
        )

    def gen(self, root):
        return {
            "define_params": self.get_define_params(root),
            "define_ions": self.get_define_ions(root),
            "ion_symbol": self.get_ion_symbol(root)
        }

    def get_define_params(self, root):
        code = ""
        cnt = 0
        ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
                for x in children_of_type('UseIon', root)]
        params = [x.name for x in children_of_type('Range', root)[0].ranges] +\
            children_of_type('Nonspecific', root)[0].nonspecifics +\
            [x.name for x in children_of_type('State', root)[0].state_vars] +\
            ["D{0}".format(x.name)
             for x in children_of_type('State', root)[0].state_vars] +\
            reduce(lambda x, y: x+y, ions) +\
            ['v', '_g']
        for param in params:
            code += "#define {0} _p[{1}]\n".format(param, cnt)
            cnt += 1
        return code

    def get_ion_symbol(self, root):
        code = ""
        for ion in children_of_type('UseIon', root):
            code += "\tstatic Symbol* _{0}_sym;\n".format(ion.ion)
        return code

    def get_define_ions(self, root):
        code = ""
        cnt = 0
        for ion in children_of_type('UseIon', root):
            read_name = ion.r[0].reads[0].name
            write_name = ion.w[0].writes[0].name
            code += "#define _ion_{0} *_ppvar[{1}]._pval\n"\
                    "#define _ion_{2} *_ppvar[{3}]._pval\n"\
                    "#define _ion_d{4}dv *_ppvar[{5}]._pval\n"\
                    .format(read_name,
                            cnt * 3,
                            write_name,
                            cnt * 3 + 1,
                            write_name,
                            cnt * 3 + 2)
            cnt += 1
        return code

    def compile(self, filename, root):
        tokens = self.gen(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

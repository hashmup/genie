import re
from functools import reduce
from jinja2 import Environment, FileSystemLoader
from os.path import join, dirname, abspath
from textx.model import children_of_type, parent_of_type


ROOT = abspath(dirname(__file__))
exponential_exp = re.compile("(?P<b>\d+)e(?P<e>\d+)")


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
            "hoc_parm_limits": self.get_hoc_parm_limits(root),
            "hoc_parm_units": self.get_hoc_parm_units(root),
            "hoc_global_param": self.get_hoc_global_param(root),
            "num_global_param": self.get_num_global_param(root),
            "define_global_param": self.get_define_global_param(root),
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

    def get_hoc_parm_limits(self, root):
        code = ""
        for parm in children_of_type('ParDef', root):
            if parm.llim and parm.ulim:
                llim = parm.llim
                ulim = parm.ulim
                mllim = exponential_exp.match(parm.llim)
                mulim = exponential_exp.match(parm.ulim)
                if mllim:
                    llim = "{0}e+{1:02d}"\
                           .format(mllim.group("b"), int(mllim.group("e")))
                if mulim:
                    ulim = "{0}e+{1:02d}"\
                           .format(mulim.group("b"), int(mulim.group("e")))
                code += "\t\"{0}_{1}\", {2}, {3},\n"\
                        .format(parm.name, self.filename, llim, ulim)
        code += "\t\"usetable_{0}\", 0, 1,// TODO: figure out what this is"\
                "\t0, 0, 0"\
                .format(self.filename)
        return code

    def get_hoc_parm_units(self, root):
        code = ""
        for assigned in children_of_type('Assigned', root)[0].assigneds:
            if assigned.unit:
                code += "\t\"{0}_{1}\", \"{2}\",\n"\
                    .format(assigned.name, self.filename, assigned.unit)
        code += "\t0,0"
        return code

    def get_hoc_global_param(self, root):
        code = ""
        for param in children_of_type('Global', root)[0].globals:
            code += "\t\"{0}_{1}\", &{0}_{1},\n"\
                    .format(param.name, self.filename)
        code += "\t\"usetable_{0}\", &usetable_{0},\n"\
                "\t0, 0"\
                .format(self.filename)
        return code

    def get_num_global_param(self, root):
        params = children_of_type('Global', root)[0].globals
        return "{0}".format(len(params))

    def get_define_global_param(self, root):
        code = ""
        cnt = 0
        for param in children_of_type('Global', root)[0].globals:
            code += "#define {0}_{1} _thread1data[{2}]\n"\
                    "#define {0} _thread[_gth]._pval[{2}]\n"\
                    .format(param.name, self.filename, cnt)
            cnt += 1
        code += "#define usetable usetable_{0}\n".format(self.filename)
        return code

    def compile(self, filename, root):
        self.filename = filename
        tokens = self.gen(root)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

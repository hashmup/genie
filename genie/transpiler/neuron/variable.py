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
        self.version = "6.2.0"

    def gen(self, root, macro_table):
        return {
            "define_params": self.get_define_params(root),
            "define_ions": self.get_define_ions(root),
            "hoc_parm_limits": self.get_hoc_parm_limits(root),
            "hoc_parm_units": self.get_hoc_parm_units(root),
            "hoc_global_param": self.get_hoc_global_param(root),
            "num_global_param": self.get_num_global_param(root),
            "define_global_param": self.get_define_global_param(root),
            "static_global": self.get_static_global(root),
            "num_states": self.get_num_states(root),
            "num_cvode": self.get_num_cvode(root),
            "mechanism": self.get_mechanism(root),
            "restruct_table": self.get_restruct_table(root),
            "optimize_table": self.get_optimize_table(root, macro_table),
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
            code += "static Symbol* _{0}_sym;\n".format(ion.ion)
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
        code += "\t\"usetable_{0}\", 0, 1,// TODO: figure out what this is\n"\
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

    def get_num_states(self, root):
        return "{0}".format(len(children_of_type('State', root)[0].state_vars))

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
        cnt = 0
        code = "#define _gth 0\n"
        for param in children_of_type('Global', root)[0].globals:
            code += "#define {0}_{1} _thread1data[{2}]\n"\
                    "#define {0} _thread[_gth]._pval[{2}]\n"\
                    .format(param.name, self.filename, cnt)
            cnt += 1
        code += "#define usetable usetable_{0}\n".format(self.filename)
        return code

    def get_static_global(self, root):
        code = ""
        for param in children_of_type('Global', root)[0].globals:
            code += "static double *_t_{0};\n".format(param.name)
        return code

    def get_mechanism(self, root):
        code = "\t\"{0}\"\n"\
               "\t\"{1}\"\n"\
               .format(self.version, self.filename)
        for parm in children_of_type('Range', root)[0].ranges:
            code += "\t\"{0}_{1}\",\n"\
                    .format(parm.name, self.filename)
        for parm in children_of_type('Nonspecific', root)[0].nonspecifics:
            code += "\t\"{0}_{1}\",\n"\
                    .format(parm, self.filename)
        for parm in children_of_type('State', root)[0].state_vars:
            code += "\t\"{0}_{1}\",\n"\
                    .format(parm.name, self.filename)
        code += "\t0"
        return code

    def get_restruct_table(self, root):
        cnt = 0
        params = children_of_type('Global', root)[0].globals
        # code = "#ifdef RESTRUCT_TABLE\n"\
        code = "#define TABLE_SIZE 201\n"\
               "FLOAT {0}_table[TABLE_SIZE][{1}];\n"\
               .format(self.filename, len(params))
        for param in params:
            code += "#define TABLE_{0}(x) {1}_table[(x)][{2}]\n"\
                    .format(param.name.upper(), self.filename, cnt)
            cnt += 1
        # code += "#else\n"
        # for param in params:
        #     code += "#define TABLE_{0}(x) _t_{1}[(x)]\n"\
        #             .format(param.name.upper(), param.name)
        # code += "#endif\n"
        return code

    def get_optimize_table(self, root, macro_table):
        code = ""
        ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
                for x in children_of_type('UseIon', root)]
        params = [x.name for x in children_of_type('Range', root)[0].ranges] +\
            children_of_type('Nonspecific', root)[0].nonspecifics +\
            [x.name for x in children_of_type('State', root)[0].state_vars] +\
            ['v', 'g'] +\
            reduce(lambda x, y: x+y, ions)
        # if we have ordered table, then we use it first
        # then add the remainings at the end
        if macro_table:
            code = ""
            for i in range(len(macro_table)):
                code += "static double opt_table{0}"\
                        "[BUFFER_SIZE * MAX_NTHREADS][{1}];\n"\
                        .format(i, len(macro_table[i]))
                for j in range(len(macro_table[i])):
                    code += "#define TABLE_{0}(x) "\
                            "opt_table{1}[(x)][{2}]\n"\
                            .format(macro_table[i][j].upper(), i, j)
                    if macro_table[i][j] in params:
                        params.remove(macro_table[i][j])
        for param in params:
            code += "static double _{0}_table[BUFFER_SIZE * MAX_NTHREADS];\n"\
                    .format(param)
        return code

    def get_num_cvode(self, root):
        return "{0}".format(len(children_of_type('UseIon', root)) * 3)

    def compile(self, filename, root, table_order):
        self.filename = filename
        tokens = self.gen(root, table_order)
        tokens.update({"filename": filename}.items())
        return self.jinja_template.render(**tokens)

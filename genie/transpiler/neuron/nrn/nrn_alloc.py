from collections import defaultdict
from textx.model import children_of_type, parent_of_type


class NrnAlloc():
    def __init__(self):
        pass

    def gen(self, root):
        return {
            "param_size": self.get_param_size(root),
            "init_range_parameter": self.get_init_range_prameter(root),
            "num_prop_ion": self.get_num_prop_ion(root),
            "connect_ionic_variables": self.get_connect_ionic_variables(root)
        }

    def get_param_size(self, root):
        """
        " Param size equals to sum of followings,
        " Range parameter ex. gnabar, gkbar
        " Non specific current ex. il
        " ion (read / write) ex. ena, ina
        " state (original + differencial) ex. m, dm
        " common variable? (TODO: make sure what is this) v, _g
        """
        param_size = \
            len(children_of_type('Range', root)[0].ranges) + \
            len(children_of_type('Nonspecific', root)[0].nonspecifics) + \
            len(children_of_type('UseIon', root)) * 2 + \
            len(children_of_type('State', root)[0].state_vars) * 2 + \
            + 2
        return "{0}".format(param_size)

    def get_init_range_prameter(self, root):
        code = ""
        for par in children_of_type('ParDef', root):
            code += "\t{0} = {1};\n".format(par.name, float(par.value))
        return code

    def get_num_prop_ion(self, root):
        ions = children_of_type('UseIon', root)
        return "{0}".format(len(ions) * 3 + 1)

    def get_connect_ionic_variables(self, root):
        code = ""
        cnt = 0
        for ion in children_of_type('UseIon', root):
            read_name = ion.r[0].reads[0].name
            write_name = ion.w[0].writes[0].name
            code += "\tprop_ion = need_memb(_{0}_sym);\n"\
                    "\tnrn_promote(prop_ion, 0, 1);\n"\
                    "\t_ppvar[{1}]._pval = &prop_ion->param[0]; /* {2} */\n"\
                    "\t_ppvar[{3}]._pval = &prop_ion->param[3]; /* {4} */\n"\
                    "\t_ppvar[{5}]._pval = &prop_ion->param[4];"\
                    "/* _ion_d{6}dv */\n"\
                    .format(ion.ion,
                            cnt * 3,
                            read_name,
                            cnt * 3 + 1,
                            write_name,
                            cnt * 3 + 2,
                            write_name)
            cnt += 1
        return code

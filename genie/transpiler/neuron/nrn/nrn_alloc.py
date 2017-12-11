from collections import defaultdict
from textx.model import children_of_type, parent_of_type


class NrnAlloc():
    def __init__(self):
        pass

    def gen(self, root):
        return {
            "init_range_parameter": self.get_init_range_prameter(root)
        }

    def get_init_range_prameter(self, root):
        code = ""
        for par in children_of_type('ParDef', root):
            code += "\t{0} = {1};\n".format(par.name, float(par.value))
        return code

from functools import reduce
from collections import defaultdict
from textx.model import children_of_type, parent_of_type


class NrnCur():
    def __init__(self):
        pass

    def gen(self, root):
        return {
            "link_table": self.get_link_table(root)
        }

    def get_link_table(self, root):
        code = ""
        params = [x.name for x in children_of_type('Range', root)[0].ranges] +\
            children_of_type('Nonspecific', root)[0].nonspecifics +\
            [x.name for x in children_of_type('State', root)[0].state_vars] +\
            ['v', 'g']
        for param in params:
            code += "\tdouble* {0}_table ="\
                    " &(_{0}_table[BUFFER_SIZE * _nth->_id]);\n"\
                    .format(param)
        # code += "#ifndef KPLUS_WITHOUT_SHARED_CURRENT\n"
        ions = [[x.r[0].reads[0].name, x.w[0].writes[0].name]
                for x in children_of_type('UseIon', root)]
        for ion in reduce(lambda x, y: x+y, ions):
            code += "\tdouble* {0}_table ="\
                    " &(_{0}_table[BUFFER_SIZE * _nth->_id]);\n"\
                    .format(ion)
        # code += "#endif\n"
        return code

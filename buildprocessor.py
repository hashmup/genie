from collections import defaultdict
from buildgenerator import BuildGenerator


class BuildProcessor():
    def __init__(self, param_dict):
        self.build_param_dict = param_dict["build"]
        self.build_config_param_dict = param_dict["build_config"]
        self.build_generator = BuildGenerator()
        self.make_table()
        self.done = False

    def make_table_(self, dict_):
        for k in dict_:
            tmp = self.rangestr2array(dict_[k])
            if isinstance(dict_[k], list):
                self.not_iterate[k] = True
            if isinstance(tmp, defaultdict):
                for k2 in tmp:
                    self.index_table["{0}.{1}".format(k, k2)] = 0
                self.build_table[k] = tmp
                self.index_table[k] = 0
            elif tmp is not None and len(tmp) != 0:
                self.build_table[k] = tmp
                self.index_table[k] = 0

    def init(self):
        for k in self.index_table:
            self.index_table[k] = 0
        self.done = False

    def make_table(self):
        self.build_table = defaultdict(dict)
        self.index_table = defaultdict(dict)
        self.not_iterate = defaultdict(dict)
        self.make_table_(self.build_param_dict)
        self.make_table_(self.build_config_param_dict)

    def has_next(self):
        return not self.done

    def cur_params(self):
        params = defaultdict(dict)
        for k in self.index_table:
            if k not in self.build_table:
                continue
            if isinstance(self.build_table[k], defaultdict):
                params[k] = defaultdict(dict)
                for k2 in self.build_table[k]:
                    key = self.index_table["{0}.{1}".format(k, k2)]
                    params[k][k2] = self.build_table[k][k2][key]
            else:
                if k in self.not_iterate:
                    params[k] = self.build_table[k]
                else:
                    params[k] = self.build_table[k][self.index_table[k]]
        return params

    def process(self):
        params = self.cur_params()
        self.build_generator.gen(params)

        # proceed by 1
        for k in self.index_table:
            if k not in self.build_table or k in self.not_iterate:
                continue
            if isinstance(self.build_table[k], defaultdict):
                for k2 in self.build_table[k]:
                    if self.index_table["{0}.{1}".format(k, k2)] <\
                            len(self.build_table[k][k2]) - 1:
                        self.index_table["{0}.{1}".format(k, k2)] += 1
                        return
            if self.index_table[k] < len(self.build_table[k]) - 1:
                self.index_table[k] += 1
                return
        self.done = True

    def rangestr2array(self, rangestr):
        # if given str is already array then just return it.
        if isinstance(rangestr, list):
            return rangestr
        if type(rangestr) is int:
            return [rangestr]
        if isinstance(rangestr, dict):
            ret = defaultdict(dict)
            for k in rangestr:
                ret[k] = self.rangestr2array(rangestr[k])
            return ret
        params = rangestr.split(',')
        if len(params) > 1:
            params = [int(x.replace(' ', '')) for x in params]
            if len(params) == 2:
                return [x for x in range(params[0], params[1]+1)]
            if len(params) == 3:
                return [x for x in range(params[0], params[1]+1, params[2])]
        return [rangestr]

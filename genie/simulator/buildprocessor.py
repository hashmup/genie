from collections import defaultdict
from utils.env import Environment


class BuildProcessor():
    def __init__(self, param_dict):
        self.env = Environment()
        self.build_config_name = 'build_config_{0}'.format(self.env.get_env())
        self.build_param_dict = param_dict["build"]
        self.build_config_param_dict = param_dict[self.build_config_name]
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
                    self.build_table["{0}.{1}".format(k, k2)] = tmp[k2]
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
            pos = k.find(".")
            if pos != -1:
                key1 = k[:pos]
                key2 = k[pos+1:]
                if key1 not in params:
                    params[key1] = defaultdict(dict)
                index = self.index_table[k]
                params[key1][key2] = self.build_table[k][index]
            else:
                if k in self.not_iterate:
                    params[k] = self.build_table[k]
                else:
                    params[k] = self.build_table[k][self.index_table[k]]
        if params["compile_options"]["CC"] == "mpicc":
            params["compile_options"]["CXX"] = "mpic++"
        else:
            params["compile_options"]["CXX"] = "mpiicpc"
        params["compile_options"]["MPICC"] = params["compile_options"]["CC"]
        params["compile_options"]["MPICXX"] = params["compile_options"]["CXX"]
        return params

    def carry_by_one(self, carry_index):
        keys = list(self.index_table.keys())
        for j in range(carry_index + 1):
            self.index_table[keys[j]] = 0
        if carry_index + 1 == len(keys):
            self.done = True
            return
        j = carry_index + 1
        while j < len(keys) and\
                (len(self.build_table[keys[j]]) <= 1 or
                 keys[j] in self.not_iterate):
            j += 1
        if j < len(keys):
            if self.index_table[keys[j]] == len(self.build_table[keys[j]]) - 1:
                # self.carry = True
                self.carry_by_one(j)
            else:
                self.index_table[keys[j]] += 1
        else:
            self.done = True

    def process(self):
        params = self.cur_params()
        # proceed by 1
        keys = list(self.index_table.keys())
        for i in range(len(keys)):
            if keys[i] not in self.not_iterate and\
                    self.index_table[keys[i]] < len(self.build_table[keys[i]]):
                if self.index_table[keys[i]] ==\
                        len(self.build_table[keys[i]]) - 1:
                    self.carry_by_one(i)
                    return
                self.index_table[keys[i]] += 1
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
            params = [x.replace(' ', '') for x in params]
            isDigit = True
            for i in range(len(params)):
                if params[i].isdigit():
                    params[i] = int(params[i])
                else:
                    isDigit = False
            if isDigit:
                if len(params) == 2:
                    return [x for x in range(params[0], params[1]+1)]
                if len(params) == 3:
                    return [x for x in range(params[0], params[1]+1, params[2])]
            else:
                return params
        return [rangestr]

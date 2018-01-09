from collections import defaultdict
from utils.env import Environment


class JobProcessor():
    def __init__(self, param_dict):
        self.env = Environment()
        self.job_name = 'job_{0}'.format(self.env.get_env())
        self.jobparam_dict = param_dict[self.job_name]
        self.build_table()
        self.done = False

    def build_table(self):
        self.job_table = defaultdict(dict)
        self.index_table = defaultdict(dict)
        for k in self.jobparam_dict:
            tmp = self.rangestr2array(self.jobparam_dict[k])
            if tmp is not None and len(tmp) != 0:
                self.job_table[k] = tmp
                self.index_table[k] = 0

    def init(self):
        for k in self.index_table:
            self.index_table[k] = 0
        self.done = False

    def has_next(self):
        return not self.done

    def cur_params(self):
        params = defaultdict(dict)
        for k in self.index_table:
            params[k] = self.job_table[k][self.index_table[k]]
        return params

    def carry_by_one(self, carry_index):
        keys = list(self.index_table.keys())
        for j in range(carry_index + 1):
            self.index_table[keys[j]] = 0
        if carry_index + 1 == len(keys):
            self.done = True
            return
        j = carry_index + 1
        while j < len(keys) and len(self.job_table[keys[j]]) <= 1:
            j += 1
        if j < len(keys):
            if self.index_table[keys[j]] == len(self.job_table[keys[j]]) - 1:
                # self.carry = True
                self.carry_by_one(j)
            else:
                self.index_table[keys[j]] += 1
        else:
            self.done = True

    def process(self):
        params = self.cur_params()

        # proceed by 1
        # if self.curry:
        #     self.curry = False
        #     return
        keys = list(self.index_table.keys())
        for i in range(len(keys)):
            if self.index_table[keys[i]] < len(self.job_table[keys[i]]):
                if self.index_table[keys[i]] ==\
                        len(self.job_table[keys[i]]) - 1:
                    self.carry_by_one(i)
                    return
                self.index_table[keys[i]] += 1
                return

    def rangestr2array(self, rangestr):
        # if given str is already array then just return it.
        if isinstance(rangestr, list):
            return rangestr
        if type(rangestr) is int:
            return [rangestr]
        params = rangestr.split(',')
        if len(params) > 1:
            params = [int(x.replace(' ', '')) for x in params]
            if len(params) == 2:
                return [x for x in range(params[0], params[1]+1)]
            if len(params) == 3:
                return [x for x in range(params[0], params[1]+1, params[2])]
        return [rangestr]

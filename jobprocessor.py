from collections import defaultdict
from jobgenerator import JobGenerator


class JobProcessor():
    def __init__(self, param_dict):
        self.job_name = 'job_{}'.format(param_dict['type'])
        self.jobparam_dict = param_dict[self.job_name]
        self.job_generator = JobGenerator(self.job_name)
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

    def process(self):
        params = self.cur_params()
        self.job_generator.gen(params)

        # proceed by 1
        for k in self.index_table:
            if self.index_table[k] < len(self.job_table[k]) - 1:
                self.index_table[k] += 1
                return
        self.done = True

    def rangestr2array(self, rangestr):
        # if given str is already array then just return it.
        if rangestr isinstance(list()):
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

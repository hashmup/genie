from collections import defaultdict
from jobgenerator import JobGenerator
from processor import Processor

class JobProcessor(Processor):
  def __init__(self, param_dict):
    Processor.__init__(self)
    self.job_name = 'job_%s'%param_dict['type']
    self.jobparam_dict = param_dict[self.job_name]
    self.job_generator = JobGenerator(self.job_name)
    self.build_table()

  def build_table(self):
    self.job_table = defaultdict(dict)
    self.index_table = defaultdict(dict)
    for k in self.jobparam_dict:
        self.job_table[k] = self.rangestr2array(self.job_table[k])
        self.index_table[k] = 0
  def run(self):
    params = defaultdict(dict)
    for k in self.index_table:
        params[k] = self.job_table[k][self.index_table[k]]
    self.job_generator.gen(params)
  def rangestr2array(self, rangestr):
    # if given str is already array then just return it.
    if type(rangestr) is type(list()):
        return rangestr
    rangestr = rangestr.replace(' ', '')
    params = [int(x) for x in rangestr.split(',')]
    if len(params) == 2:
        return [x for x in range(params[0], params[1])]
    if len(params) == 3:
        return [x for x in range(params[0], params[1], prams[2])]

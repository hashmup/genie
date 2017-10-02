from generator import Generator
from fileutil import *

class JobGenerator(Generator):
  def __init__(self, params):
    self.job_name = 'job_%s'%params['type']
    Generator.__init__(self, [[self.job_name, 'sh']])
    self.params = params
  def gen(self):
    tmp = self.contents[self.job_name]['template'].render(\
        modules=self.params[self.job_name]['modules'],\
        omp_num_threads=self.params[self.job_name]['omp_num_threads'],\
        nrniv=self.params[self.job_name]['nrniv'],\
        hoc_name=self.params[self.job_name]['hoc_name'],\
        stop_time=self.params[self.job_name]['stop_time'],\
        nthread=self.params[self.job_name]['nthread'],\
        prof=self.params[self.job_name]['prof'])
    write_file(self.contents[self.job_name]['output_file'], tmp)

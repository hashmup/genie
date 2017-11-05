from generator import Generator
from fileutil import *

class JobGenerator(Generator):
  def __init__(self, job_name):
    self.job_name = job_name
    Generator.__init__(self, [[self.job_name, 'sh']])
  def gen(self, params):
    tmp = self.contents[self.job_name]['template'].render(\
        modules=params['modules'],\
        omp_num_threads=params['omp_num_threads'],\
        nrniv=params['nrniv'],\
        hoc_name=params['hoc_name'],\
        stop_time=params['stop_time'],\
        nthread=params['nthread'],\
        prof=params['prof'])
    write_file(self.contents[self.job_name]['output_file'], tmp)

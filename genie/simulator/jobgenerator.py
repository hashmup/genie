from simulator.generator import Generator
from utils.fileutil import *


class JobGenerator(Generator):
    def __init__(self, job_name):
        self.job_name = job_name
        Generator.__init__(self, [[self.job_name, 'sh']])

    def gen(self, params, cnt, use_tmp):
        nrniv_path = params['nrniv']
        if use_tmp:
            nrniv_path = nrniv_path.replace("specials", "specials.tmp")
        output = self.contents[self.job_name]['output_file']
        output = output.replace("job_cluster.sh", "job{0}.sh".format(cnt))
        output = output.replace("job_k.sh", "job{0}.sh".format(cnt))
        tmp = self.contents[self.job_name]['template'].render(
            nodes=params['nodes'],
            ppn=params['ppn'],
            proc=int(params['nodes']) * int(params['ppn']),
            modules=params['modules'],
            omp_num_threads=params['omp_num_threads'],
            nrniv=nrniv_path,
            hoc_name=params['hoc_name'],
            stop_time=params['stop_time'],
            nthread=params['nthread'],
            prof=params['prof'])
        write_file(output, tmp)

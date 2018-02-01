from pathlib import Path
import time
import re
import sys
from utils.shell import Shell
spike_exp = re.compile("SPIKE : \t (?P<val>\d+\.*\d*)\t (?P<idvec>[0-9]+) \
                       \[(?P<pid>\d+)\]")
start_exp = re.compile("\[(?P<pid>\d+)\] NC = (?P<nc>\d+), SYN = (?P<syn>\d+), \
                       tmp_pre = (?P<tmp_pre>\d+), \
                       tmp_post = (?P<tmp_post>\d+)")
end_exp = re.compile("\[(?P<pid>\d+)\] nsendmax=(?P<nsendmax>\d+) \
                     nsend=(?P<nsend>\d+) nrecv=(?P<nrecv>\d+) \
                     nrecv_useful=(?P<nrecv_useful>\d+)")
time_exp = re.compile(
    "\s+\* core time : (?P<decimal>\d+).(?P<float>\d+) sec\s+")
dir_path = "neuron_kplus/hoc/"


class Summarizer:
    """
    "
    """
    def __init__(self):
        self.shell = Shell()

    def summary(self, job_id, job_cnt):
        core_time = self.obtain_time("job{0}.sh.o{1}".format(job_cnt, job_id))

        # self.clean_up(job_type, job_id)
        self.clean_up(job_cnt, job_id)
        return core_time

    def obtain_time(self, filename):
        f_check = Path("{0}{1}".format(dir_path, filename))
        while not f_check.exists():
            time.sleep(5)
        f = open("{0}{1}".format(dir_path, filename))
        lines = f.readlines()
        f.close()
        for line in lines:
            m = time_exp.match(line)
            if m:
                calc_time = int(m.group("decimal")) +\
                    int(m.group("float")) * 10**(-len(m.group("float")))
                print(calc_time)
                return calc_time

    def clean_up(self, job_cnt, job_id):
        self.shell.execute(
            "cp",
            ["job{0}.sh.o{1} ../../tmp/".format(job_cnt, job_id)],
            [],
            dir_path
        )
        self.shell.execute(
            "cp",
            ["job{0}.sh.e{1} ../../tmp/".format(job_cnt, job_id)],
            [],
            dir_path
        )
        self.shell.execute(
            "rm",
            [
                "job{0}.sh.o{1}".format(job_cnt, job_id),
                "job{0}.sh.e{1}".format(job_cnt, job_id),
            ],
            ["-f"],
            dir_path
        )

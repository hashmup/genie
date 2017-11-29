import re
import time
from utils.shell import Shell
from summarizer import Summarizer
from collections import defaultdict
import pandas as pd
import threading

id_cluster_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")
id_k_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")
job_exp = re.compile(
    "(?P<id>\d+).\w+\s+\w+.\w+\s+\w+\s+\d+:\d+:\d+\s+(?P<state>\w+)\s+\w+\s+")


class TaskRunner:
    """
    " This class is singleton.
    " Whenever you want to assign new job, call push_job().
    " If the number of concurrent running job is under max_num_jobs,
    " we will simply deploy it.
    " In other case, we will wait other jobs to be done and then deploy
    """
    MAX_NUM_JOBS = 4

    def __init__(self, environment, neuron_path):
        self.current_job_num = 0
        self.pending_jobs = []
        self.running_jobs = []
        self.current_build_param = None
        self.shell = Shell()
        self.summarizer = Summarizer()
        self.environment = environment
        self.result_table = pd.DataFrame()
        self.lock = threading.Lock()
        self.neuron_path = neuron_path

    def push_job(self, build_param, job_param):
        self.pending_jobs.append([build_param, job_param])

    def deploy_job(self):
        if len(self.pending_jobs) > 0:
            build_param, job_param = self.pending_jobs.pop(0)
            job_id = self.deploy(self.current_build_param != build_param)
            self.current_build_param = build_param
            self.running_jobs.append(job_id)
            merge_params =\
                dict(build_param.items() +
                     job_param.items() +
                     {"job_id": job_id, "time": 0}.items())
            print(merge_params)
            for key in merge_params.keys():
                if isinstance(merge_params[key], defaultdict) or\
                        isinstance(merge_params[key], list):
                    if key not in self.result_table:
                        self.result_table.loc[-1, key] = 0
                    self.result_table[key] =\
                        self.result_table[key].astype('object')
                    self.result_table.set_value(-1, key, merge_params[key])
                else:
                    self.result_table.loc[-1, key] = merge_params[key]
            self.result_table.index = self.result_table.index + 1
            self.result_table = self.result_table.sort_index()
            print(self.result_table)

    def is_job_still_running(self, job_id):
        res = self.shell.execute("qstat", [], [], "")
        job_lines = res[0].split('\n')
        if len(job_lines) > 2:
            for line in job_lines[2:]:
                m = job_exp.match(line)
                if m is not None:
                    state = m.group("state")
                    if job_id == m.group("id") and state == "C":
                        return False
        return True

    def watch_job(self):
        print("test")
        self.lock.acquire()
        print(self.running_jobs)
        print(len(self.running_jobs))
        for i in range(len(self.running_jobs)):
            if not self.is_job_still_running(self.running_jobs[i]):
                print("complete {0}".format(self.running_jobs[i]))
                self.current_job_num -= 1
                time = self.summarizer.summary(self.environment,
                                               self.running_jobs[i])
                key = self.result_table['job_id'] == self.running_jobs[i]
                self.result_table.loc[key, 'time'] = time
                del self.running_jobs[i]
                break
        self.lock.release()
        if len(self.pending_jobs) == 0 and len(self.running_jobs) == 0:
            self.result_table.to_csv("result.csv")
            self.timer_.cancel()
            return
        self.timer_ = threading.Timer(20.0, self.watch_job)
        self.timer_.start()

    def run(self):
        t = threading.Thread(target=self.watch_job)
        t.start()
        while len(self.pending_jobs) != 0:
            if self.current_job_num > self.MAX_NUM_JOBS:
                time.sleep(20)
            while self.current_job_num < self.MAX_NUM_JOBS:
                print(self.running_jobs)
                print(self.current_job_num,
                      len(self.pending_jobs),
                      len(self.running_jobs))
                self.deploy_job()
                self.current_job_num += 1

    def run_build(self):
        commands = []
        if self.environment == "cluster":
            commands = [{
                "command": "make",
                "args": ["clean"],
                "options": [],
                "work_dir": "{0}/nrn-7.2".format(self.neuron_path)
            },
                {
                "command": "../../genie/tmp/build_config.sh",
                "args": [],
                "options": [],
                "work_dir": "{0}/nrn-7.2".format(self.neuron_path)
            },
                {
                "command": "make",
                "args": [],
                "options": [],
                "work_dir": "{0}/nrn-7.2".format(self.neuron_path)
            },
                {
                "command": "make",
                "args": ["install"],
                "options": [],
                "work_dir": "{0}/nrn-7.2".format(self.neuron_path)
            },
                {
                "command": "./make_special_x86_64.sh",
                "args": [],
                "options": [],
                "work_dir": "{0}/specials".format(self.neuron_path)
            }]
        if self.environment == "k":
            commands = [{
                "command": "../../tmp/build_config.sh",
                "args": [],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "bash",
                "args": ["../../tmp/build.sh"],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "make",
                "args": ["clean"],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "make",
                "args": [],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "make",
                "args": ["install"],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "../../tmp/build_config_tune.sh",
                "args": [],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "bash",
                "args": ["../../tmp/build.sh"],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "make",
                "args": ["clean"],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "make",
                "args": [],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "make",
                "args": ["install"],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "cp",
                "args": ["./x86_64/bin/*", "./sparc64/bin/"],
                "options": [],
                "work_dir": "neuron_kplus/exec"
            },
                {
                "command": "./make_special_sparc64.sh",
                "args": [],
                "options": [],
                "work_dir": "neuron_kplus/specials"
            }]
        self.shell.run_cmds(commands)

    def run_job(self):
        if self.environment == "cluster":
            res = self.shell.execute(
                "qsub",
                ["../../genie/tmp/job_cluster.sh"],
                [],
                "{0}/hoc".format(self.neuron_path)
            )
            m = id_cluster_exp.match(res[0])
            return m.group("id")
        if self.environment == "k":
            res = self.shell.execute(
                "psub",
                ["../../genie/tmp/job_k.sh"],
                [],
                "{0}/hoc".format(self.neuron_path)
            )
            m = id_k_exp.match(res[0])
            return m.group("id")

    def deploy(self, shouldBuild):
        if shouldBuild:
            self.run_build()
        return self.run_job()

import re
import time
from utils.shell import Shell
from simulator.summarizer import Summarizer
from simulator.verifier import Verifier
from simulator.deploycommand import DeployCommand
from collections import defaultdict
from transpiler.compiler import Compiler
import pandas as pd
import threading

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
        self.compiler = Compiler()
        self.verifier = Verifier()
        self.environment = environment
        self.result_table = pd.DataFrame()
        self.lock = threading.Lock()
        self.deployCommand = DeployCommand(neuron_path)

    def push_job(self, build_param, job_param, is_bench):
        self.pending_jobs.append([build_param, job_param, is_bench])

    def deploy_job(self):
        if len(self.pending_jobs) > 0:
            self.lock.acquire()
            build_param, job_param, is_bench = self.pending_jobs.pop(0)
            job_id = self.deploy(self.current_build_param != build_param,
                                 is_bench)
            self.current_build_param = build_param
            self.running_jobs.append(job_id)
            merge_params =\
                dict(**build_param,
                     **job_param,
                     **{"job_id": job_id, "bench": is_bench, "time": 0})
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
            self.lock.release()
            print(self.result_table)

    def is_job_still_running(self, job_id):
        res = self.shell.execute("qstat", [], [], "")[0]
        if type(res) is bytes:
            res = res.decode('utf-8')
        job_lines = res.split('\n')
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
        if len(self.running_jobs) == 0 and len(self.pending_jobs) != 0:
            print(self.pending_jobs)
            if self.verifier.verify():
                print("correct")
            self.result_table.to_csv("result.csv")
            self.timer_cancel()
            return

        if len(self.pending_jobs) == 0 and len(self.running_jobs) == 0:
            print('verifyyyyy')
            if self.verifier.verify():
                print("Correct!")
            else:
                print("Incorrect :(")
            self.result_table.to_csv("result.csv")
            self.timer_.cancel()
            return
        self.timer_ = threading.Timer(20.0, self.watch_job)
        self.timer_.start()

    def run(self):
        t = threading.Thread(target=self.watch_job)
        t.start()
        while len(self.pending_jobs) != 0:
            self.lock.acquire()
            num = self.current_job_num
            self.lock.release()
            if num > self.MAX_NUM_JOBS:
                time.sleep(20)
            while True:
                self.lock.acquire()
                num = self.current_job_num
                self.lock.release()
                if num >= self.MAX_NUM_JOBS:
                    break
                print(self.running_jobs)
                print(self.current_job_num,
                      len(self.pending_jobs),
                      len(self.running_jobs))
                self.deploy_job()
                self.lock.acquire()
                self.current_job_num += 1
                self.lock.release()
        print('aaaaaa')
        print(self.pending_jobs)
        print(self.running_jobs)
        print('yyyyyyy')

    def deploy(self, shouldBuild, is_bench):
        if shouldBuild:
            self.compiler.gen("neuron_kplus/mod/hh_k.mod")
            self.deployCommand.build(self.environment, is_bench)
        return self.deployCommand.run(self.environment)

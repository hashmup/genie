import re
import time
from utils.shell import Shell
from simulator.summarizer import Summarizer
from simulator.verifier import Verifier
from simulator.deploycommand import DeployCommand
from collections import defaultdict
from transpiler.compiler import Compiler
from datetime import datetime
import pandas as pd
import numpy as np
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
        self.pending_jobs_bak = []
        self.running_jobs = []
        self.candidate_jobs = defaultdict(dict)
        self.current_build_param = None
        self.shell = Shell()
        self.summarizer = Summarizer()
        self.compiler = Compiler()
        self.verifier = Verifier()
        self.environment = environment
        self.result_table = pd.DataFrame()
        self.lock = threading.Lock()
        self.deployCommand = DeployCommand(neuron_path)
        self.complete = False
        self.first = True
        self.cnt = 0
        self.job_total_num = 0

    def push_job(self, build_param, job_param, is_bench):
        self.pending_jobs.append([build_param, job_param, is_bench])
        self.job_total_num += 1

    def deploy_job(self):
        if len(self.pending_jobs) > 0:
            self.lock.acquire()
            build_param, job_param, is_bench = self.pending_jobs.pop(0)
            job_id = self.deploy(self.current_build_param != build_param,
                                 is_bench)
            # record params for future use
            self.candidate_jobs[job_id]["build_param"] = build_param
            self.candidate_jobs[job_id]["job_param"] = job_param
            self.candidate_jobs[job_id]["is_bench"] = is_bench

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
           # print(self.result_table)

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
        print("{0}/{1} {2}".format(self.job_total_num - len(self.pending_jobs), self.job_total_num, str(datetime.now())))
        self.lock.acquire()
        for i in range(len(self.running_jobs)):
            if not self.is_job_still_running(self.running_jobs[i]):
                #print("complete {0}".format(self.running_jobs[i]))
                self.current_job_num -= 1
                time = self.summarizer.summary(self.environment,
                                               self.running_jobs[i])
                key = self.result_table['job_id'] == self.running_jobs[i]
                if self.first or self.cnt == 0:
                    self.result_table.loc[key, 'time'] = time
                else:
                    self.result_table.loc[key, 'time'] += time
                self.complete = True
                del self.running_jobs[i]
                break
        self.lock.release()

        if len(self.pending_jobs) == 0 and len(self.running_jobs) == 0\
                and self.complete:
            print('verifyyyyy')
            if self.verifier.verify():
                print("Correct!")
            else:
                print("Incorrect :(")
            if self.first:
                self.result_table.to_csv("result_all.csv")
                self.timer_.cancel()
                self.first = False
                sorted_table = self.result_table.sort_values(by="time")\
                    .reset_index(drop=True)
                self.job_total_num = 0
                for i in range(int(len(sorted_table) / 4.0)):
                    job_id = sorted_table['job_id'][i]
                    build = self.candidate_jobs[job_id]["build_param"]
                    job = self.candidate_jobs[job_id]["job_param"]
                    is_bench = self.candidate_jobs[job_id]["is_bench"]
                    self.pending_jobs_bak\
                        .append([build, job, is_bench])
                    self.job_total_num += 1
                self.result_table = pd.DataFrame()
            elif self.cnt < 3:
                self.cnt += 1
            else:
                self.result_table['avg_time'] = self.result_table['time'] / 3.0
                self.result_table.to_csv("result_candidate.csv")
                self.timer_.cancel()
                return
            self.pending_jobs = self.pending_jobs_bak
            self.run()
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
                # print(self.running_jobs)
                # print(self.current_job_num,
                #       len(self.pending_jobs),
                #       len(self.running_jobs))
                self.deploy_job()
                self.lock.acquire()
                self.current_job_num += 1
                self.lock.release()

    def deploy(self, shouldBuild, is_bench):
        if shouldBuild:
            self.compiler.gen("neuron_kplus/mod/hh_k.mod")
            self.deployCommand.build(self.environment, is_bench)
        return self.deployCommand.run(self.environment)

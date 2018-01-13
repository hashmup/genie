import re
import time
import math
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

job_cluster_exp = re.compile(
    "(?P<id>\d+).\w+\s+\w+.\w+\s+\w+\s+\d+:\d+:\d+\s+(?P<state>\w+)\s+\w+\s+")
job_k_exp = re.compile(
    "(?P<id>\d+)\s+\w+.\w+\s+\w+\s+(?P<state>\w+)\s+[\s\w\d\[\]\/\:\-]+")


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
        self.current_bench = True
        self.shell = Shell()
        self.summarizer = Summarizer()
        self.compiler = Compiler()
        self.verifier = Verifier()
        self.environment = environment
        self.result_table = pd.DataFrame()
        self.lock = threading.Lock()
        self.relation_table = defaultdict(dict)
        self.relation_table_job_cnt = defaultdict(dict)
        self.deployCommand = DeployCommand(neuron_path)
        self.job_cnt = 0
        self.use_tmp = True  # We use both original and tmp
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
            shouldBuild = self.current_build_param != build_param or\
                self.current_bench != is_bench
            job_id = self.deploy(shouldBuild,
                                 build_param,
                                 job_param,
                                 is_bench)
            self.relation_table_job_cnt[job_id] = self.job_cnt
            if self.first:
                # record params for future use
                self.candidate_jobs[job_id]["build_param"] = build_param
                self.candidate_jobs[job_id]["job_param"] = job_param
                self.candidate_jobs[job_id]["is_bench"] = is_bench
            else:
                for key in self.candidate_jobs:
                    build = self.candidate_jobs[key]["build_param"]
                    job = self.candidate_jobs[key]["job_param"]
                    bench = self.candidate_jobs[key]["is_bench"]
                    if build == build_param\
                        and job == job_param\
                            and bench == is_bench:
                                self.relation_table[job_id] = key
            self.current_build_param = build_param
            self.current_bench = is_bench
            self.running_jobs.append(job_id)
            if self.first:
                merge_params =\
                    dict(**build_param,
                         **job_param,
                         **{"job_id": job_id, "bench": is_bench, "time": 0})
                for key in merge_params.keys():
                    if isinstance(merge_params[key], defaultdict) or\
                            isinstance(merge_params[key], list) or\
                            isinstance(merge_params[key], dict):
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

    def is_job_still_running(self, job_id):
        if self.environment == "cluster":
            res = self.shell.execute("qstat", [], [], "")[0]
            if type(res) is bytes:
                res = res.decode('utf-8')
            job_lines = res.split('\n')
            if len(job_lines) > 2:
                for line in job_lines[2:]:
                    m = job_cluster_exp.match(line)
                    if m is not None:
                        state = m.group("state")
                        if job_id == m.group("id"):
                            if state == "C":
                                return False
                            else:
                                return True
            return True
        elif self.environment == "k":
            res = self.shell.execute("pjstat", [], [], "")[0]
            if type(res) is bytes:
                res = res.decode('utf-8')
            job_lines = res.split('\n')
            if len(job_lines) > 2:
                for line in job_lines[2:]:
                    m = job_k_exp.match(line)
                    if m is not None:
                        state = m.group("state")
                        if job_id == m.group("id"):
                            return True
            return False

    def watch_job(self):
        print("{0}/{1} {2}".format(self.job_total_num - len(self.pending_jobs),
                                   self.job_total_num, str(datetime.now())))
        self.lock.acquire()
        for i in range(len(self.running_jobs)):
            if not self.is_job_still_running(self.running_jobs[i]):
                # print("complete {0}".format(self.running_jobs[i]))
                self.current_job_num -= 1
                job_cnt = self.relation_table_job_cnt[self.running_jobs[i]]
                time = self.summarizer.summary(self.running_jobs[i], job_cnt)
                if self.first:
                    key = self.result_table['job_id'] == self.running_jobs[i]
                else:
                    key = self.result_table['job_id'] ==\
                          self.relation_table[self.running_jobs[i]]
                if self.first:
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
                    .reset_index(drop=True)[:math.ceil(len(sorted_table)/4.0)]
                self.job_total_num = 0
                self.result_table = sorted_table.sort_values(by="bench")
                for i in range(sorted_table):
                    job_id = sorted_table['job_id'][i]
                    build = self.candidate_jobs[job_id]["build_param"]
                    job = self.candidate_jobs[job_id]["job_param"]
                    is_bench = self.candidate_jobs[job_id]["is_bench"]
                    self.pending_jobs_bak.append([build, job, is_bench])
                    self.job_total_num += 1
            elif self.cnt < 3:
                self.timer_.cancel()
                self.cnt += 1
            else:
                self.result_table['avg_time'] = self.result_table['time'] / 4.0
                self.result_table.to_csv("result_candidate.csv")
                self.timer_.cancel()
                return
            self.pending_jobs = self.pending_jobs_bak[:]
            self.run()
            return
        self.timer_ = threading.Timer(5.0, self.watch_job)
        self.timer_.start()

    def run(self):
        t = threading.Thread(target=self.watch_job)
        t.start()
        while len(self.pending_jobs) != 0:
            self.lock.acquire()
            num = self.current_job_num
            self.lock.release()
            if num > self.MAX_NUM_JOBS:
                time.sleep(5)
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

    def deploy(self, shouldBuild, build_params, job_params, is_bench):
        if shouldBuild:
            self.use_tmp = not self.use_tmp
            self.compiler.gen("neuron_kplus/mod/hh_k.mod")
            self.deployCommand.build(self.environment,
                                     is_bench,
                                     build_params,
                                     self.use_tmp)
        self.job_cnt += 1
        return self.deployCommand.run(self.environment,
                                      job_params,
                                      self.job_cnt,
                                      self.use_tmp)

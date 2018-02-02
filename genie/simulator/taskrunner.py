import re
import time
import math
import os
import random
from utils.shell import Shell
from simulator.summarizer import Summarizer
from simulator.verifier import Verifier
from simulator.deploycommand import DeployCommand
from collections import defaultdict
from transpiler.compiler import Compiler
from transpiler.analyzer import Analyzer
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
        self.running_jobs = defaultdict(dict)
        self.candidate_jobs = defaultdict(dict)
        self.current_build_param = None
        self.current_bench = True
        self.macro_table = True
        self.shell = Shell()
        self.summarizer = Summarizer()
        self.compiler = Compiler()
        self.analyzer = Analyzer()
        self.verifier = Verifier()
        self.environment = environment
        self.result_table = pd.DataFrame()
        self.compile_lock = threading.Lock()
        self.current_lock = threading.Lock()
        self.pending_lock = threading.Lock()
        self.running_lock = threading.Lock()
        self.relation_table = defaultdict(dict)
        self.relation_table_job_cnt = defaultdict(dict)
        self.deployCommand = DeployCommand(neuron_path)
        self.neuron_path = neuron_path
        self.job_cnt = 0
        self.use_tmp = True  # We use both original and tmp
        self.complete = False
        self.first = True
        self.cnt = 0
        self.job_total_num = 0

    def push_job(self, build_param, job_param, is_bench, macro_table):
        self.pending_jobs.append(
            [build_param, job_param, is_bench, macro_table])
        self.job_total_num += 1

    def deploy_job(self):
        self.pending_lock.acquire()
        num = len(self.pending_jobs)
        self.pending_lock.release()
        if num > 0:
            self.compile_lock.acquire()
            self.pending_lock.acquire()
            build_param, job_param, is_bench, macro_table =\
                self.pending_jobs.pop(0)
            shouldBuild = self.current_build_param != build_param or\
                self.current_bench != is_bench or\
                self.current_macro_table != macro_table
            self.current_build_param = build_param
            self.current_bench = is_bench
            self.current_macro_table = macro_table
            self.pending_lock.release()
            self.compile_lock.release()
            job_id = self.deploy(shouldBuild,
                                 build_param,
                                 job_param,
                                 is_bench,
                                 macro_table)
            self.relation_table_job_cnt[job_id] = self.job_cnt
            if self.first:
                # record params for future use
                self.candidate_jobs[job_id]["build_param"] = build_param
                self.candidate_jobs[job_id]["job_param"] = job_param
                self.candidate_jobs[job_id]["is_bench"] = is_bench
                self.candidate_jobs[job_id]["macro_table"] = macro_table
            else:
                for key in self.candidate_jobs:
                    build = self.candidate_jobs[key]["build_param"]
                    job = self.candidate_jobs[key]["job_param"]
                    bench = self.candidate_jobs[key]["is_bench"]
                    macro = self.candidate_jobs[key]["macro_table"]
                    if build == build_param\
                        and job == job_param\
                            and bench == is_bench\
                            and macro == macro_table:
                                self.relation_table[job_id] = key
            self.running_lock.acquire()
            self.running_jobs[job_id] = 0
            # self.running_jobs.append(job_id)
            if self.first:
                merge_params =\
                    dict(**build_param,
                         **job_param,
                         **{"job_id": job_id,
                            "bench": is_bench,
                            "macro": macro_table,
                            "time": 0})
                for key in merge_params.keys():
                    if isinstance(merge_params[key], defaultdict) or\
                            isinstance(merge_params[key], list) or\
                            isinstance(merge_params[key], tuple) or\
                            isinstance(merge_params[key], dict):
                        if key not in self.result_table:
                            self.result_table.loc[-1, key] = 0
                        self.result_table[key] =\
                            self.result_table[key].astype('object')
                        if isinstance(merge_params[key], defaultdict) or isinstance(merge_params[key], dict):
                            self.result_table.set_value(-1, key, frozenset(merge_params[key].items()))
                        else:
                            self.result_table.set_value(-1, key, frozenset(merge_params[key]))
                    else:
                        self.result_table.loc[-1, key] = merge_params[key]
                self.result_table.index = self.result_table.index + 1
                self.result_table = self.result_table.sort_index()
            self.running_lock.release()

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
                                if self.running_jobs[job_id] == 0:
                                    self.running_jobs[job_id] = 1
                                return True
            if self.running_jobs[job_id] > 0:
                return False
            else:
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
                            if self.running_jobs[job_id] == 0:
                                self.running_jobs[job_id] = 1
                            return True
            if self.running_jobs[job_id] > 0:
                return False
            else:
                return True

    def watch_job(self):
        while True:
            print("{0}: {1}/{2} {3}".format(self.cnt, self.job_total_num - len(self.pending_jobs),
                                       self.job_total_num, str(datetime.now())))
            self.running_lock.acquire()
            for job_id in self.running_jobs:
                if not self.is_job_still_running(job_id):
                    # print("complete {0}".format(self.running_jobs[i]))
                    job_cnt = self.relation_table_job_cnt[job_id]
                    calc_time = self.summarizer.summary(job_id, job_cnt)
                    if self.first:
                        key = self.result_table['job_id'] == job_id
                    else:
                        key = self.result_table['job_id'] ==\
                              self.relation_table[job_id]
                    if self.first:
                        self.result_table.loc[key, 'time'] = calc_time
                    else:
                        self.result_table.loc[key, 'time{0}'.format(self.cnt)] = calc_time
                        #self.result_table.loc[key, 'time'] += calc_time
                    self.complete = True
                    del self.running_jobs[job_id]
                    self.current_job_num -= 1
                    break
            self.running_lock.release()

            self.pending_lock.acquire()
            if len(self.pending_jobs) == 0 and len(self.running_jobs) == 0\
                    and self.complete:
                print(self.cnt)
                print('verifyyyyy')
                if self.verifier.verify():
                    print("Correct!")
                else:
                    print("Incorrect :(")
                if self.first:
                    self.result_table.to_csv("result_all.csv")
                    self.first = False
                    index = math.ceil(len(self.result_table)/1.0)
                    sorted_table = self.result_table.sort_values(by="time")\
                        .reset_index(drop=True)[:index]
                    sorted_table = sorted_table.sort_values(by=["bench", "macro", "compile_options"])\
                        .reset_index(drop=True)
                    self.job_total_num = 0
                    self.result_table = sorted_table
                    for i in range(len(sorted_table)):
                        job_id = sorted_table['job_id'][i]
                        build = self.candidate_jobs[job_id]["build_param"]
                        job = self.candidate_jobs[job_id]["job_param"]
                        is_bench = self.candidate_jobs[job_id]["is_bench"]
                        macro_table = self.candidate_jobs[job_id]["macro_table"]
                        self.pending_jobs_bak.append([build,
                                                      job,
                                                      is_bench,
                                                      macro_table])
                        self.job_total_num += 1
                elif self.cnt < 4:
                    self.cnt += 1
                else:
                    #self.result_table['avg_time'] = self.result_table['time'] / 3.0
                    self.result_table.to_csv("result_candidate.csv")
                    self.pending_lock.release()
                    self.cleanup()
                    return
                self.pending_jobs = self.pending_jobs_bak[:]
                self.current_job_num = 0
                self.pending_lock.release()
                self.run()
                return
            self.pending_lock.release()
            time.sleep(10)

    def run(self):
        threading.Thread(target=self.watch_job).start()
        while len(self.pending_jobs) != 0:
            self.current_lock.acquire()
            num = self.current_job_num
            self.current_lock.release()
            if num > self.MAX_NUM_JOBS:
                time.sleep(15)
            while True:
                self.current_lock.acquire()
                num = self.current_job_num
                if num >= self.MAX_NUM_JOBS or num >= self.job_total_num:
                    self.current_lock.release()
                    break
                threading.Thread(target=self.deploy_job).start()
                self.current_job_num += 1
                time.sleep(200)
                self.current_lock.release()

    def deploy(self,
               shouldBuild,
               build_params,
               job_params,
               is_bench,
               macro_table):
        _use_tmp = self.use_tmp
        if shouldBuild:
            self.compile_lock.acquire()
            self.use_tmp = not self.use_tmp
            _use_tmp = self.use_tmp
            path = "neuron_kplus/mod/hh_k.mod"
            if is_bench or not len(macro_table):
                macro_table = None
            self.compiler.gen(path, macro_table)
            self.deployCommand.build(self.environment,
                                     is_bench,
                                     build_params,
                                     _use_tmp)
        else:
            self.compile_lock.acquire()
        self.job_cnt += 1
        job_id = self.deployCommand.run(self.environment,
                                        job_params,
                                        self.job_cnt,
                                        _use_tmp)
        self.compile_lock.release()
        return job_id

    def cleanup(self):
        root = os.path.join(self.neuron_path, "../")
        dir_path = os.path.join(os.path.join(root, "data"), datetime.now().strftime('%Y-%m-%d_%H-%M'))
        os.makedirs(dir_path)
        self.shell.execute(
            "mv",
            ["tmp", dir_path],
            [],
            root
        )
        self.shell.execute(
            "mv",
            ["result_all.csv", dir_path],
            [],
            root
        )
        self.shell.execute(
            "mv",
            ["result_candidate.csv", dir_path],
            [],
            root
        )

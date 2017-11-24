import re
import time
from shell import Shell
import threading

id_cluster_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")
id_k_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")
job_exp = re.compile("(?P<id>\d+).\w+\s+\w+.\w+\s+\w+\s+\d+:\d+:\d+\s+(?P<state>\w+)\s+\w+\s+")
class TaskRunner:
    """
    " This class is singleton.
    " Whenever you want to assign new job, call push_job().
    " If the number of concurrent running job is under max_num_jobs, we will simply deploy it
    " In other case, we will wait other jobs to be done and then deploy
    """
    MAX_NUM_JOBS = 4
    def __init__(self, environment):
        self.current_job_num = 0
        self.pending_jobs = []
        self.running_jobs = []
        self.current_build_param = None
        self.shell = Shell()
        self.environment = environment
    def push_job(self, build_param, job_param):
        self.pending_jobs.append([build_param, job_param])
    def deploy_job(self):
        if len(self.pending_jobs) > 0:
            build_param, job_param = self.pending_jobs.pop(0)
            job_id = self.deploy(self.current_build_param != build_param)
            self.current_build_param = build_param
            self.running_jobs.append(job_id)
    def is_job_still_running(self, job_id):
        res = self.shell.execute("qstat", [], [], "")
        job_lines = res[0].split('\n')
        if len(job_lines) > 2:
            for line in job_lines[2:]:
                m = job_exp.match(line)
                if m is not None:
                    print(m.group("state"), m.group("id"))
                    state = m.group("state")
                    if job_id == m.group("id") and state == "C":
                        return False
        return True
    def watch_job(self):
        print("test")
        for i in range(len(self.running_jobs)):
            if not self.is_job_still_running(self.running_jobs[i]):
                print("complete %s"%self.running_jobs[i])
                self.current_job_num -= 1
                del self.running_jobs[i]
        if len(self.pending_jobs) == 0 and len(self.running_jobs) == 0:
            self.timer_.cancel()
        self.timer_ = threading.Timer(3.0, self.watch_job)
        self.timer_.start()
    def run(self):
        t = threading.Thread(target=self.watch_job)
        t.start()
        while len(self.pending_jobs) != 0:
            if self.current_job_num > self.MAX_NUM_JOBS:
                time.sleep(20)
            while self.current_job_num < self.MAX_NUM_JOBS:
                print(self.running_jobs)
                print(self.current_job_num, len(self.pending_jobs), len(self.running_jobs))
                self.deploy_job()
                self.current_job_num += 1
    def run_build(self):
        commands = []
        if self.environment == "cluster":
            commands = [{
                "command":"make",
                "args":["clean"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.2"
            },
            {
                "command":"../../tmp/build_config.sh",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.2"
            },
            {
                "command":"make",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.2"
            },
            {
                "command":"make",
                "args":["install"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.2"
            },
            {
                "command":"./make_special_x86_64.sh",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/specials"
            }]
        if self.environment == "k":
            commands = [{
                "command":"../../tmp/build_config.sh",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"bash",
                "args":["../../tmp/build.sh"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"make",
                "args":["clean"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"make",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"make",
                "args":["install"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"../../tmp/build_config_tune.sh",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"bash",
                "args":["../../tmp/build.sh"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"make",
                "args":["clean"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"make",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"make",
                "args":["install"],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
            {
                "command":"cp",
                "args":["./x86_64/bin/*", "./sparc64/bin/"],
                "options":[],
                "work_dir": "neuron_kplus/exec"
            },
            {
                "command":"./make_special_sparc64.sh",
                "args":[],
                "options":[],
                "work_dir": "neuron_kplus/specials"
            }]
        self.shell.run_cmds(commands)
    def run_job(self):
        if self.environment == "cluster":
            res = self.shell.execute(
                "qsub",
                ["../../tmp/job_cluster.sh"],
                [],
                "neuron_kplus/hoc"
            )
            m = id_cluster_exp.match(res[0])
            return m.group("id")
        if self.environment == "k":
            res = self.shell.execute(
                "psub",
                ["../../tmp/job_k.sh"],
                [],
                "neuron_kplus/hoc"
            )
            m = id_k_exp.match(res[0])
            return m.group("id")
    def deploy(self, shouldBuild):
        if shouldBuild:
            self.run_build()
        return self.run_job()

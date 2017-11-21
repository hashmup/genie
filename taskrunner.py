from shell import Shell

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
        if len(self.pending_jobs) > 0
            build_param, job_param = self.pending_jobs.pop(0)
            self.build_generator.gen(build_param)
            self.job_generator.gen(job_param)
            job_id = self.deploy(self.current_build_param == build_param)
            self.current_build_param = build_param
            self.running_jobs.append(job_id)
    def watch_job(self):
        for i in len(self.running_jobs):
            if not self.is_job_still_running(self.running_jobs[i]):
                del self.running_jobs[i]
        if len(self.pending_jobs) == 0 and len(self.running_jobs) == 0:
            self.timer_.cancel()
    def run(self):
        self.timer_ = threading.Timer(5.0, self.watch_job).start()
        while self.current_job_num < MAX_NUM_JOBS:
            self.deploy_job()
            self.current_job_num += 1
            sleep(10)
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
                "command":"./make_special_sparc64.sh",
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
            print(res)
        if self.environment == "k":
            res = self.shell.execute(
                "psub",
                ["../../tmp/job_k.sh"],
                [],
                "neuron_kplus/hoc"
            )
            print(res)
    def deploy(self, shouldBuild):
        if shouldBuild:
            self.run_build()
        self.run_job()

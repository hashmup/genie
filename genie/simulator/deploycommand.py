import re
from utils.shell import Shell
from utils.env import Environment
from simulator.buildgenerator import BuildGenerator
from simulator.jobgenerator import JobGenerator


id_cluster_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")
id_k_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")


class DeployCommand():
    def __init__(self, neuron_path):
        self.env = Environment()
        self.job_name = 'job_{0}'.format(self.env.get_env())
        self.shell = Shell()
        self.neuron_path = neuron_path
        self.build_generator = BuildGenerator()
        self.job_generator = JobGenerator(self.job_name)

    def build(self, env, bench, params, use_tmp):
        self.build_generator.gen(params, use_tmp)
        commands = []
        tmp_str = ".tmp" if use_tmp else ""
        if env == "cluster":
            commands = [{
                "command": "make",
                "args": ["clean"],
                "options": [],
                "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path, tmp_str)
            },
                {
                "command": "../../genie/simulator/tmp/build_config.sh",
                "args": [],
                "options": [],
                "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path, tmp_str)
            },
                {
                "command": "make",
                "args": [],
                "options": [],
                "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path, tmp_str)
            },
                {
                "command": "make",
                "args": ["install"],
                "options": [],
                "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path, tmp_str)
            },
                {
                "command": "./make_special_x86_64.sh",
                "args": [bench],
                "options": [],
                "work_dir": "{0}/specials{1}".format(self.neuron_path, tmp_str)
            }]
        if env == "k":
            commands = [{
                "command": "make",
                "args": ["clean"],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "../../genie/simulator/tmp/build_config.sh",
                "args": [],
                "options":[],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "bash",
                "args": ["../../genie/simulator/tmp/build.sh"],
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
                "command": "../../genie/simulator/tmp/build_config_tune.sh",
                "args": [],
                "options": [],
                "work_dir": "neuron_kplus/nrn-7.3"
            },
                {
                "command": "bash",
                "args": ["../../genie/simulator/tmp/build.sh"],
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

    def run(self, env, params, cnt, use_tmp):
        self.job_generator.gen(params, cnt, use_tmp)
        if env == "cluster":
            res = self.shell.execute(
                "qsub",
                ["../../genie/simulator/tmp/job{0}.sh".format(cnt)],
                [],
                "{0}/hoc".format(self.neuron_path)
            )[0]
            if type(res) is bytes:
                res = res.decode('utf-8')
            m = id_cluster_exp.match(res)
            return m.group("id")
        elif env == "k":
            res = self.shell.execute(
                "psub",
                ["../../genie/simulator/tmp/job{0}.sh".format(cnt)],
                [],
                "{0}/hoc".format(self.neuron_path)
            )[0]
            if type(res) is bytes:
                res = res.decode('utf-8')
            m = id_k_exp.match(res)
            return m.group("id")

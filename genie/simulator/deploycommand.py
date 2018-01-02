import re
from utils.shell import Shell

id_cluster_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")
id_k_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")


class DeployCommand():
    def __init__(self, neuron_path):
        self.shell = Shell()
        self.neuron_path = neuron_path

    def build(self, env, bench):
        commands = []
        if env == "cluster":
            commands = [{
                "command": "make",
                "args": ["clean"],
                "options": [],
                "work_dir": "{0}/nrn-7.2".format(self.neuron_path)
            },
                {
                "command": "../../genie/simulator/tmp/build_config.sh",
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
                "args": [bench],
                "options": [],
                "work_dir": "{0}/specials".format(self.neuron_path)
            }]
        if env == "k":
            commands = [{
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

    def run(self, env):
        if env == "cluster":
            res = self.shell.execute(
                "qsub",
                ["../../genie/simulator/tmp/job_cluster.sh"],
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
                ["../../genie/simulator/tmp/job_k.sh"],
                [],
                "{0}/hoc".format(self.neuron_path)
            )[0]
            if type(res) is bytes:
                res = res.decode('utf-8')
            m = id_k_exp.match(res)
            return m.group("id")

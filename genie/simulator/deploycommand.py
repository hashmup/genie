import re
import threading
from utils.shell import Shell
from utils.env import Environment
from simulator.buildgenerator import BuildGenerator
from simulator.jobgenerator import JobGenerator


id_cluster_exp = re.compile("(?P<id>[0-9]+).\w+.\w+")
id_k_exp = re.compile("\[INFO\]\s+PJM\s+\d+\s+\w+\s+\w+\s(?P<id>\d+)\s+\w+.")


class DeployCommand():
    def __init__(self, neuron_path):
        self.env = Environment()
        self.shell = Shell()
        self.neuron_path = neuron_path
        job_name = 'job_{0}'.format(self.env.get_env())
        self.build_generator = BuildGenerator()
        self.job_generator = JobGenerator(job_name)

    def build(self, env, bench, params, use_tmp, build_neuron, neuron_use_tmp):
        self.build_generator.gen(params, use_tmp, neuron_use_tmp, env)
        commands = []
        tmp_str = ".tmp" if use_tmp else ""
        if env == "cluster":
            if build_neuron:
                commands.append({
                    "command": "make",
                    "args": ["clean"],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "../../genie/simulator/tmp/build_config.sh",
                    "args": [],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "make",
                    "args": [],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "make",
                    "args": ["install"],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
            commands.append({
                "command": "./make_special.sh",
                "args": ["x86_64", bench, tmp_str],
                "options": [],
                "work_dir": "{0}/specials{1}".format(self.neuron_path, tmp_str)
            })
        if env == "k":
            if build_neuron:
                commands.append({
                    "command": "../config/do_config_k1.sh",
                    "args": [],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "make",
                    "args": [],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "make",
                    "args": ["install"],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "../../genie/simulator/tmp/build_config.sh",
                    "args": [],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "export",
                    "args": ["LANG=C"],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "export",
                    "args": ["LC_ALL=C"],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "make",
                    "args": [],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "make",
                    "args": ["install"],
                    "options": [],
                    "work_dir": "{0}/nrn-7.2{1}".format(self.neuron_path,
                                                        tmp_str)
                })
                commands.append({
                    "command": "cp",
                    "args": ["./x86_64/bin/*", "./sparc64/bin/"],
                    "options": [],
                    "work_dir": "{0}/exec{1}".format(self.neuron_path, tmp_str)
                })
            commands.append({
                "command": "./make_special.sh",
                "args": [],
                "options": ["sparc64", bench, tmp_str],
                "work_dir": "{0}/specials{1}".format(self.neuron_path, tmp_str)
            })
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
                "pjsub",
                ["../../genie/simulator/tmp/job{0}.sh".format(cnt)],
                [],
                "{0}/hoc".format(self.neuron_path)
            )[0]
            if type(res) is bytes:
                res = res.decode('utf-8')
            m = id_k_exp.match(res)
            return m.group("id")

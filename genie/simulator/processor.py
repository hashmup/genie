import inspect
from simulator.configparser import ConfigParser
from simulator.buildprocessor import BuildProcessor
from simulator.jobprocessor import JobProcessor
from simulator.taskrunner import TaskRunner
from utils.env import Environment
from utils.shell import Shell


class Processor():
    def __init__(self, config_path, neuron_path):
        self.env = Environment()
        build, job = self.parseConfigFile(config_path)
        self.buildProcessor = BuildProcessor(build)
        self.jobProcessor = JobProcessor(job)
        self.shell = Shell()
        self.setup(neuron_path)
        self.taskRunner = TaskRunner(self.env.get_env(), neuron_path)

    def parseConfigFile(self, path):
        config = ConfigParser(path).parse()
        return config['build'], config['job']

    def run_(self, is_bench):
        self.taskRunner.push_job(
            self.buildProcessor.cur_params(),
            self.jobProcessor.cur_params(),
            is_bench
        )

    def caller_name(self, skip=2):
        stack = inspect.stack()
        start = 0 + skip
        if len(stack) < start + 1:
            return ''
        parentframe = stack[start][0]
        name = []
        module = inspect.getmodule(parentframe)
        if module:
            name.append(module.__name__)
        if 'self' in parentframe.f_locals:
            name.append(parentframe.f_locals['self'].__class__.__name__)
        codename = parentframe.f_code.co_name
        if codename != '<module>':  # top level usually
            name.append(codename)  # function or a method
        del parentframe
        return ".".join(name)

    def run(self):
        s = inspect.stack()
        print("me", inspect.stack()[1][3])
        print("module", inspect.getmodulename(s[1][1]))
        print("dad", self.caller_name())
        for is_bench in [True, False]:
            self.buildProcessor.init()
            while self.buildProcessor.has_next():
                self.buildProcessor.process()
                self.jobProcessor.init()
                while self.jobProcessor.has_next():
                    self.jobProcessor.process()
                    self.run_(is_bench)
        self.taskRunner.run()

    def setup(self, neuron_path):
        """
        " We need to setup all the dir, files before starting job
        """
        # setup tmp/
        self.shell.execute(
            "mkdir",
            ["../tmp/"],
            ["-p"],
            neuron_path
        )
        # setup copy of neuron dir
        # we need to do this so that we don't have to wait
        # while we are building, o/w we cannot deploy a job
        # we need to copy neuron_kplus/nrn-7.x and neuron_kplus/specials
        nrn_path = "{0}/nrn-7.2".format(neuron_path)
        specials_path = "{0}/specials".format(neuron_path)
        print(self.shell.execute(
            "cp",
            [nrn_path, "{0}.tmp".format(nrn_path)],
            ["-r"]
        ))
        print(self.shell.execute(
            "cp",
            [specials_path, "{0}.tmp".format(specials_path)],
            ["-r"]
        ))

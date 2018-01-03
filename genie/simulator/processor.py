import inspect
from simulator.configparser import ConfigParser
from simulator.buildprocessor import BuildProcessor
from simulator.jobprocessor import JobProcessor
from simulator.taskrunner import TaskRunner
from utils.env import Environment


class Processor():
    def __init__(self, config_path, neuron_path):
        self.env = Environment()
        build, job = self.parseConfigFile(config_path)
        self.buildProcessor = BuildProcessor(build)
        self.jobProcessor = JobProcessor(job)
        self.taskRunner = TaskRunner(self.env.get_env(), neuron_path)
        self.run()
        self.taskRunner.run()

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
            print("call Processor.run")
            self.buildProcessor.init()
            while self.buildProcessor.has_next():
                self.buildProcessor.process()
                self.jobProcessor.init()
                while self.jobProcessor.has_next():
                    self.jobProcessor.process()
                    self.run_(is_bench)

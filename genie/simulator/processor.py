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

    def run(self):
        for is_bench in [True, False]:
            print("call Processor.run")
            self.buildProcessor.init()
            while self.buildProcessor.has_next():
                self.buildProcessor.process()
                self.jobProcessor.init()
                while self.jobProcessor.has_next():
                    self.jobProcessor.process()
                    self.run_(is_bench)

from configparser import ConfigParser
from buildprocessor import BuildProcessor
from jobprocessor import JobProcessor
from taskrunner import TaskRunner


class Processor():
    def __init__(self, config_path, neuron_path):
        build, job = self.parseConfigFile(config_path)
        self.buildProcessor = BuildProcessor(build)
        self.jobProcessor = JobProcessor(job)
        self.taskRunner = TaskRunner(job['type'], neuron_path)
        self.run()
        self.taskRunner.run()

    def parseConfigFile(self, path):
        config = ConfigParser(path).parse()
        return config['build'], config['job']

    def run_(self):
        self.taskRunner.push_job(
            self.buildProcessor.cur_params(),
            self.jobProcessor.cur_params()
        )

    def run(self):
        while self.buildProcessor.has_next():
            self.buildProcessor.process()
            self.jobProcessor.init()
            while self.jobProcessor.has_next():
                self.jobProcessor.process()
                self.run_()

from configparser import ConfigParser
from buildprocessor import BuildProcessor
from jobprocessor import JobProcessor
class Processor():
  def __init__(self, path):
    build, job = self.parseConfigFile(path)
    self.buildProcessor = BuildProcessor(build)
    self.jobProcessor = JobProcessor(job)
    self.run()
  def parseConfigFile(self, path):
    config = ConfigParser(path).parse()
    return config['build'], config['job']
  def run_(self):
    """
    " return process_id
    """
    return 0
  def summarize(self, process_id):
    pass
  def run(self):
    while self.buildProcessor.has_next():
      self.buildProcessor.process()
      self.jobProcessor.init()
      while self.jobProcessor.has_next():
        self.jobProcessor.process()
        process_id = self.run_()
        self.summarize(process_id)

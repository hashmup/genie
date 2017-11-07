#!/usr/bin/env python
"""
Automatically test the parameters given in config file to optimize code
"""

from argparse import ArgumentParser
from configparser import ConfigParser
from processor import Processor
class Genie():
  def __init__(self, args=None):
    self.args = args

  def check_config(self):
    if self.args.config is None:
        return False
    self.config = ConfigParser(self.args.config).parse()
    return self.config is not None

  def run(self):
    if self.check_config():
      self.processor = Processor(self.args.config)
      self.processor.run()

def parse_args():
  parser = ArgumentParser(description=__doc__)
  parser.add_argument("config")
  args = parser.parse_args()

  return args

if __name__ == '__main__':
    args = parse_args()
    Genie(args=args).run()

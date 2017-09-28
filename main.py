#!/usr/bin/env python
"""
Automatically test the parameters given in config file to optimize code
"""

from argparse import ArgumentParser

class Genie():
  def __init__(self, args=None):
    self.args = args
  def run(self):
    print(self.args.config)
    pass

def parse_args():
  parser = ArgumentParser(description=__doc__)
  parser.add_argument("config")
  args = parser.parse_args()

  return args

if __name__ == '__main__':
    args = parse_args()
    Genie(args=args).run()

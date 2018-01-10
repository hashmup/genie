#!/usr/bin/env python

from argparse import ArgumentParser
from os.path import join, dirname, abspath
from genie.genie import Genie


ROOT = abspath(dirname(__file__))


def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("config")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    neuron_path = join(ROOT, 'neuron_kplus')
    Genie(neuron_path, args=args).run()

#!/usr/bin/env python

from argparse import ArgumentParser
from genie.genie import Genie


def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("config")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    Genie("../neuron_kplus", args=args).run()

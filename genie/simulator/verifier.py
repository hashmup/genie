from utils.shell import Shell
from os import listdir
from os.path import isfile, join
import re


spike_exp = re.compile(
    "SPIKE : \t (?P<val>\d+\.*\d*)\t (?P<idvec>[0-9]+) \[(?P<pid>\d+)\]")
start_exp = re.compile(
    "\[(?P<pid>\d+)\] NC = (?P<nc>\d+), SYN = (?P<syn>\d+), \
    tmp_pre = (?P<tmp_pre>\d+), tmp_post = (?P<tmp_post>\d+)")
end_exp = re.compile(
    "\[(?P<pid>\d+)\] nsendmax=(?P<nsendmax>\d+) nsend=(?P<nsend>\d+) \
    nrecv=(?P<nrecv>\d+) nrecv_useful=(?P<nrecv_useful>\d+)")
dir_path = "tmp/"


class Verifier():
    def __init__(self):
        self.shell = Shell()

    def verify(self):
        s = set()
        files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for filename in files:
            f = open(join(dir_path, filename))
            lines = f.readlines()
            f.close()
            s.add(self.sort_and_hash_log(lines))
        print(len(s))
        return len(s) == 1

    def sort_and_hash_log(self, lines):
        _lines = []
        start = {}
        end = {}
        spike = {}
        maxid = 0
        for line in lines:
            m = start_exp.match(line)
            if m:
                pid = int(m.group("pid"))
                start[pid] = line
                maxid = max(maxid, pid)
                continue
            m = spike_exp.match(line)
            if m:
                pid = int(m.group("pid"))
                idvec = int(m.group("idvec"))
                if pid in spike:
                    spike[pid][idvec] = line
                else:
                    spike[pid] = {}
                    spike[pid][idvec] = line
                continue
            m = end_exp.match(line)
            if m:
                pid = int(m.group("pid"))
                end[pid] = line
        if maxid > 0:
            maxid += 1
        for pid in range(maxid):
            _lines.append(start[pid])
            for line in spike[pid]:
                _lines.append(spike[pid][line])
                _lines.append(end[pid])
        return hash(tuple(_lines))

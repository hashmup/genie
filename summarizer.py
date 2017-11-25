import re, sys
spike_exp = re.compile("SPIKE : \t (?P<val>\d+\.*\d*)\t (?P<idvec>[0-9]+) \[(?P<pid>\d+)\]")
start_exp = re.compile("\[(?P<pid>\d+)\] NC = (?P<nc>\d+), SYN = (?P<syn>\d+), tmp_pre = (?P<tmp_pre>\d+), tmp_post = (?P<tmp_post>\d+)")
end_exp = re.compile("\[(?P<pid>\d+)\] nsendmax=(?P<nsendmax>\d+) nsend=(?P<nsend>\d+) nrecv=(?P<nrecv>\d+) nrecv_useful=(?P<nrecv_useful>\d+)")
time_exp = re.compile("\s+* core time : (?P<decimal>\d+).(?P<float>\d+) sec\s+")
dir_path = "neuron_kplus/hoc/"
class Summarizer:
    """
    "
    """
    def __init__(self):
        pass
    def summary(self, job_type, job_id):
        time = self.obtain_time("job_%s.sh.o%d"%(job_type, job_id))
        self.clean_up(job_type, job_id)
        return time
    def check_correctness(self, filename):
        f = open(filename)
        _lines = f.readlines()
        f.close()
        lines = _lines[:12]
        start = {}
        end = {}
        spike = {}
        maxid = 0
        for line in _lines:
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
            lines.append(start[pid])
            for line in spike[pid]:
                lines.append(spike[pid][line])
            lines.append(end[pid])
        f = open("sort_{0}".format(filename), 'w')
        for line in lines:
            f.write(line)
        f.close()
    def obtain_time(self, filename):
        f = open(filename)
        lines = f.readlines()
        f.close()
        for line in lines:
            m = time_exp.match(line)
            if m:
                time = int(m.group("decimal")) + int(m.group("float")) * 10**(-len(m.group("float")+1))
                return time
    def clean_up(self, job_type, job_id):
        self.shell.execute(
            "rm",
            [
                "%sjob_%s.sh.o%d"%(dir_path, job_type, job_id),
                "%sjob_%s.sh.e%d"%(dir_path, job_type, job_id),
            ],
            ["-f"],
            dir_path
        )

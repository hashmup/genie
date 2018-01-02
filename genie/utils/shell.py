import os
from subprocess import PIPE, Popen, STDOUT


class Shell:
    """
    " This class is used to run shell command.
    """
    def __init__(self):
        pass

    def run_cmds(self, commands):
        for command in commands:
            self.execute(
                command["command"],
                command["args"],
                command["options"],
                command["work_dir"]
            )

    def execute(self, command, args, options, work_dir=''):
        """
        " Run: command args in work_dir
        " ex. (ls, ["../"], [-a]) => ls ../ -a
        "
        " Return: [stdout, stderr]
        """
        cmd = self.make_cmd(command, args, options)
        cwd = work_dir
        if work_dir == '':
            cwd = os.path.dirname(os.path.realpath(__file__))
        process = Popen(
            args=cmd,
            stdout=PIPE,
            stderr=PIPE,
            cwd=cwd,
            shell=True
        )
        return process.communicate()

    def parse_args(self, args):
        ret = ""
        if args is None:
            return ret
        ret += " ".join([str(v) for v in args])
        return ret

    def parse_options(self, options):
        ret = ""
        if options is None:
            return ret
        ret += " ".join([str(v) for v in options])
        return ret

    def make_cmd(self, command, args, options):
        return "{0} {1} {2}".format(
            command,
            self.parse_args(args),
            self.parse_options(options))

import re
from utils.shell import Shell


class Environment():
    def __init__(self):
        self.shell = Shell()

    def get_os(self):
        """
            Add a new architecture to this function.
        """
        # k: if k_accountj exists
        test_k = self.shell.execute("k_accountj", [], [], "")[0]
        if type(test_k) is bytes:
            test_k = test_k.decode('utf-8')
        if test_k != '':
            return "k"

        test_os = self.shell.execute("uname", [], [], "")[0].lower().rstrip()
        if type(test_os) is bytes:
            test_os = test_os.decode('utf-8')
        if test_os == 'darwin':
            return "osx"
        if test_os == 'linux':
            # centos + ubuntu
            test_linux = self.shell.execute("lsb_release", [], ['-a'], "")[0]
            if type(test_linux) is bytes:
                test_linux = test_linux.decode('utf-8')
            exp = re.compile("Distributor ID:\t(?P<os>\w+)\n")
            index = test_linux.find("Distributor")
            if index == -1:
                return "unkown"
            m = exp.match(test_linux[index:])
            return m.group("os").lower()

        return "unknown"

    def get_env(self):
        os = self.get_os()
        print(os)
        if os == "k":
            return "k"
        elif os != "unknown":
            return "cluster"
        else:
            return "unknown"

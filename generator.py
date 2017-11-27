from collections import defaultdict
from os.path import join, dirname, abspath
from jinja2 import Environment, FileSystemLoader
from fileutil import *

ROOT = abspath(dirname(__file__))


class Generator():
    def __init__(self, files):
        self.contents = defaultdict(dict)
        self.jinja_env = Environment(
            loader=FileSystemLoader(join(ROOT, 'template'))
        )
        self.setup_dir()
        for i in range(len(files)):
            filename, extension = files[i]
            self.contents[filename]['template'] =
            self.jinja_env.get_template("{0}.{1}".format(filename, extension))
            self.contents[filename]['output_file'] =
            join(join(ROOT, 'tmp'), '{0}.{1}'.format(filename, extension))

    def setup_dir(self):
        mkdir(join(ROOT, 'tmp'))

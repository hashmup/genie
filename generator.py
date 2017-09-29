from os.path import join, dirname, abspath
from jinja2 import Environment, FileSystemLoader

ROOT = abspath(dirname(__file__))

class Generator():
  def __init__(self, filename):
    self.job = job
    self.jinja_env = Environment(loader=FileSystemLoader(join(ROOT, 'template')))
    self.template = self.jinja_env.get_template(filename)

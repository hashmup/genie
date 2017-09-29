import os
def write_file(path, text):
  with open(path, 'w') as f:
    f.write(text)

def isdir(path):
  return os.path.isdir(path)

def isfile(path):
  return os.path.isfile(path)

def mkdir(path):
  if not isdir(path):
    os.mkdir(path)

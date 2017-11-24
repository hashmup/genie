import os
import stat

def write_file(path, text):
  flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
  mode = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
  umask_original = os.umask(0)
  try:
    os.remove(path)
  except OSError:
    pass
  try:
    fdesc = os.open(path, flags, mode)
  finally:
    os.umask(umask_original)
  with os.fdopen(fdesc, 'w') as f:
    f.write(text)

def isdir(path):
  return os.path.isdir(path)

def isfile(path):
  return os.path.isfile(path)

def mkdir(path):
  if not isdir(path):
    os.mkdir(path)

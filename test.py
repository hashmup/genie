from taskrunner import TaskRunner
tr = TaskRunner('cluster')
tr.run_build()
print(tr.run_job())

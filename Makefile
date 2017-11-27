all: run
pull:
	bash scripts/pull.sh
clean-pyc:
	rm -rf *.pyc
	rm -rf *.pyo
clean-dir:
	rm -rf tmp
clean-log:
	rm -rf neuron_kplus/hoc/job_*.sh.*
	rm -rf result.csv
clean-cache:
	rm -rf __pycache__
clean:  clean-dir clean-pyc clean-log

run: clean
	python main.py example/job.json

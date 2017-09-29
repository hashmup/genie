all: run
clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +
clean-dir:
	rm -rf tmp
clean: clean-pyc clean-dir

run: clean
	python main.py example/job.json

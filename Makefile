all: run
pull:
	bash scripts/pull.sh
clean-pyc:
	find . -name '*.pyc' -exec rm -f{} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
clean-dir:
	rm -rf tmp
clean:  clean-dir

run: clean
	python main.py example/job.json

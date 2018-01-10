all: run

pull:
	bash scripts/pull.sh

install:
	bash scripts/setup_libraries.sh

clean-pyc:
	rm -rf *.pyc
	rm -rf *.pyo
	rm -rf genie/*.pyc
	rm -rf genie/*.pyo

clean-dir:
	rm -rf genie/tmp
	rm -rf genie/simulator/tmp
	rm -rf neuron_kplus/nrn-7.2.tmp
	rm -rf neuron_kplus/specials.tmp

clean-log:
	rm -rf neuron_kplus/hoc/job_*.sh.*
	rm -rf result.csv
	rm -rf result_all.csv
	rm -rf result_candidate.csv
	rm -rf tmp

clean-cache:
	rm -rf __pycache__

clean:  clean-dir clean-pyc clean-log

run: clean
	python main.py example/job.json

test: clean
	python main.py example/test.json
compile:
	python genie/transpiler_test.py

push: clean
	git add -A
	git commit
	git push origin master

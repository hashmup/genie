#!/bin/sh
(cd {{ neuron_path }} && make clean)
(cd {{ neuron_path }} && {{ config_path }})
(cd {{ neuron_path }} && make)
(cd {{ neuron_path }} && make install)
(cd {{ specials_path }} && ./make_special_{{ os }}.sh)

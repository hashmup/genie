#!/bin/sh
(cd {{ neuron_path }} && make clean)
(cd {{ neuron_path }} && {{ config_path }})
(cd {{ neuron_path }} && make && make install)
(cd {{ specials_path }} && ./make_special_x86_64.sh)

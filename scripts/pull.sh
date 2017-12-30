#!/bin/sh
pullIfNotExist() {
    if [ ! -d "neuron_kplus" ]; then
        git clone git@github.com:hashmup/neuron_k.git
    fi
}
pullIfNotExist

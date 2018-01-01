#!/bin/sh
pullIfNotExist() {
    if [ ! -d "neuron_kplus" ]; then
        git clone git@github.com:hashmup/neuron_k.git neuron_kplus
        mkdir -p neuron_kplus/nrn-7.2/src/npy24
        mkdir -p neuron_kplus/nrn-7.2/src/npy25
        mkdir -p neuron_kplus/nrn-7.2/src/npy26
        mkdir -p neuron_kplus/nrn-7.2/src/npy27
    else
        (cd neuron_kplus &&
        git checkout . &&
        git pull origin master)
    fi
}
pullIfNotExist

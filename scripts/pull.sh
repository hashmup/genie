#!/bin/sh
pullIfNotExist() {
    if [ ! -d "neuron_kplus" ]; then
        git clone git@github.com:DaisukeMiyamoto/neuron_kplus.git
    fi
}
pullIfNotExist

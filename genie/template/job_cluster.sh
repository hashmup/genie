#!/bin/sh
#PBS -l nodes={{ nodes }}:ppn={{ ppn }}
#PBS -q cluster
{% for module in modules -%}
module load {{ module }}
{% endfor -%}
export OMP_NUM_THREADS={{ omp_num_threads }}
NRNIV="{{ nrniv }}"
HOC_NAME="{{ hoc_name }}"
NRNOPT=\
" -c MODEL=2"\
" -c NSTIM_POS=1"\
" -c NSTIM_NUM=400"\
" -c NCELLS=256"\
" -c NSYNAPSE=10"\
" -c SYNAPSE_RANGE=1"\
" -c NETWORK=1"\
" -c STOPTIME={{ stop_time }}"\
" -c NTHREAD={{ nthread }}"\
" -c MULTISPLIT=0"\
" -c SPIKE_COMPRESS=0"\
" -c CACHE_EFFICIENT=1"\
" -c SHOW_SPIKE=1"
LPG="lpgparm -t 4MB -s 4MB -d 4MB -h 4MB -p 4MB"
MPIEXEC="mpiexec -mca mpi_print_stats 1"
PROF="{{ prof }}"
cd $PBS_O_WORKDIR
echo "${PROF} ${MPIEXEC} ${NRNIV} ${NRNOPT} ${HOC_NAME}"
time ${PROF} ${MPIEXEC} ${NRNIV} ${NRNOPT} ${HOC_NAME}

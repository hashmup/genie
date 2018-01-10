#!/bin/bash

FLAGS="-Kfast,openmp,ocl,optmsg=2"\
" -Nrt_tune,src,sta"\
" -DKPLUS -DKPLUS_FADVANCE"\
" -DKPLUS_USE_FADVANCE_OMP"\
" -DKPLUS_USE_FAPP_RANGE -DKPLUS_USE_FIPP_RANGE"\
" -DKPLUS_GATHER_SCATTER -DKPLUS_SPAWN"\
" -DARCH_K -DKPLUS_SOLVE -DKPLUS_TREESET -DKPLUS_CAP_JACOB -DKPLUS_EION"\

#" -DKPLUS_DEBUG_MPISPIKE"\
#" -DKPLUS_USE_MOD_OMP"\

./configure --prefix=$(cd ../; pwd)/exec/                             \
    --without-x --without-nmodl                                       \
    --without-nrnoc-x11 --without-x                                   \
    --host=sparc64-unknown-linux-gnu --build=x86_64-unknown-linux-gnu \
    --enable-shared=no --enable-static=yes                            \
    --with-paranrn --with-mpi --with-multisend                        \
    linux_nrnmech=no use_pthread=no                                   \
    CC=mpifccpx CXX=mpiFCCpx MPICC=mpifccpx MPICXX=mpiFCCpx           \
    CFLAGS="${FLAGS}" \
    CXXFLAGS="${FLAGS}" \

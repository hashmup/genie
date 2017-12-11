NEURON {
  SUFFIX m02
  RANGE a
}

STATE {
  a a1
}

INITIAL {
  a = 1
  a1 = 2
}

BREAKPOINT {
  SOLVE zstates METHOD cnexp
}

DERIVATIVE zstates {
  a' = a1
  a1' = a
}

from .transpiler.compiler import Compiler


def main():
    compiler = Compiler()
    compiler.gen("./neuron_kplus/mod/hh_k.mod")


if __name__ == "__main__":
    main()

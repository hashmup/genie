from transpiler.compiler import Compiler
from transpiler.analyzer import Analyzer


def main():
    path = "./neuron_kplus/mod/hh_k.mod"
    compiler = Compiler()
    analyzer = Analyzer()
    macro_table = analyzer.get_table_candidate(path)
    macro_table = None
    compiler.gen(path, macro_table)


if __name__ == "__main__":
    main()

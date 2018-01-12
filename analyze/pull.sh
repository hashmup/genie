mkdir -p dummy
rm -rf dummy/*
scp cluster:~/genie/result_all.csv dummy/
scp cluster:~/genie/result_candidate.csv dummy/

mkdir -p cluster
mkdir -p k
# scp -r cluster:~/genie/data/*/result* data/
# rsync -a --exclude=~/genie/data/*/tmp cluster:~/genie/data data/
rsync -av  --include="result*.csv" --include="job*.json" --include="*/" --exclude="*" --exclude="tmp/" cluster:~/genie/data cluster/
rsync -av  --include="result*.csv" --include="job*.json" --include="*/" --exclude="*" --exclude="tmp/" kkk:~/genie/data k/

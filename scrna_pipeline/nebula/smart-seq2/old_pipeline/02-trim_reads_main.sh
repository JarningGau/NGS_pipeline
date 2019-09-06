home=~/pipeline/scrna
project=MouseGonocyte2019
tso_fa="$home/reference/TSO.fa"
polyA_fa="$home/reference/adapters_polyAnT.fa"
cd "$home/scripts"
python 02-trim_reads.py $home $project $tso_fa $polyA_fa 24 8
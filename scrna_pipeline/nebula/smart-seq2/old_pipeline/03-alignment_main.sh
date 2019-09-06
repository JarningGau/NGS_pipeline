home=~/pipeline/scrna
project=MouseGonocyte2019
reference=~/reference/mm10/STARIndexERCC/gencode.vM21
cd "$home/scripts"
python 03-alignment.py $home $project $reference 24 8
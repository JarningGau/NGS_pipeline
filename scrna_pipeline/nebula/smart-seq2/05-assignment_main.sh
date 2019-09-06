home=~/pipeline/scrna
project=MouseGonocyte2019
gene_gtf=~/reference/mm10/Annotation/gencode.vM21.withERCC92.gtf
TE_gtf=~/reference/mm10/Annotation/mm10_rmsk_TE.gtf
cd "$home/scripts"
python 05-assign_reads.py $home $project $gene_gtf $TE_gtf 24 16
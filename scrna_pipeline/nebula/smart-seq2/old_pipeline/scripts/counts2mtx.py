import sys
import pandas as pd
import numpy as np


barcode_file = sys.argv[1]
summary_file = sys.argv[2]
file_in = sys.argv[3]
file_out = sys.argv[4]


barcodes = [l.rstrip() for l in open(barcode_file).readlines()]
gene_ids = []
with open(summary_file) as fi:
    fi.readline()
    fi.readline()
    for line in fi:
        fields = line.rstrip().split("\t")
        gene_ids.append(fields[0])

h = {}
with open(file_in) as fi:
    for line in fi:
        fields = line.rstrip().split("\t")
        gene_id = fields[0]
        barcode = fields[1]
        if gene_id not in h: h[gene_id] = {}
        h[gene_id][barcode] = int(fields[2])

nrow = len(gene_ids)
ncol = len(barcodes)
mtx = pd.DataFrame(np.zeros((nrow, ncol), dtype=int))
mtx.columns = barcodes
mtx.index = gene_ids

for gene_id in h.keys():
    ht = h[gene_id]
    for barcode in ht.keys():
        mtx[barcode][gene_id] = ht[barcode]

mtx.to_csv(file_out, sep="\t")
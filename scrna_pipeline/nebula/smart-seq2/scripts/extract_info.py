import sys
import re


file_in = sys.argv[1]

with open(file_in) as fi:
    fi.readline()
    for line in fi:
        fields = line.strip().split("\t")
        if len(fields[0].split("_")) != 3:
            continue
        barcode = fields[0].split("_")[1]
        gene_id = fields[3]
        count = fields[-2]
        unique_id = fields[-1]
        line_cache = "\t".join([gene_id, barcode, unique_id, count])
        print(line_cache)
import sys


counts = {}

if len(sys.argv) > 1:
    file_in = sys.argv[1]
    with open(file_in) as fi:
        for line in fi:
            fields = line.strip().split("\t")
            key = "\t".join(fields[0:2])
            counts[key] = counts.get(key, 0) + int(fields[-1])
else:    
    for line in sys.stdin:
        fields = line.strip().split("\t")
        key = "\t".join(fields[0:2])
        counts[key] = counts.get(key, 0) + int(fields[-1])

for key in sorted(counts.keys()):
    print("%s\t%s" % (key, counts[key]))
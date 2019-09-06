from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
barcode_file = sys.argv[3]
threads = int(sys.argv[4])

def umi_counts(path, experiment):
    file_in = os.path.join(path, "%s.gene.dedup.group.tsv" % experiment)
    file_out = os.path.join(path, "%s.gene_counts.txt" % experiment)
    cmd1 = "python extract_info.py %s | uniq | python umi_counts.py > %s" % (file_in, file_out)
    file_in = os.path.join(path, "%s.TE.dedup.group.tsv" % experiment)
    file_out = os.path.join(path, "%s.TE_counts.txt" % experiment)
    cmd2 = "python extract_info.py %s | uniq | python umi_counts.py > %s" % (file_in, file_out)
    file_in = os.path.join(path, "%s.gene_counts.txt" % experiment)
    file_out = os.path.join(path, "%s.gene_counts.mtx" % experiment)
    summary_file = os.path.join(path, "%s.gene_assigned" % experiment)
    cmd3 = "python counts2mtx.py %s %s %s %s" % (barcode_file, summary_file, file_in, file_out)
    file_in = os.path.join(path, "%s.TE_counts.txt" % experiment)
    file_out = os.path.join(path, "%s.TE_counts.mtx" % experiment)
    summary_file = os.path.join(path, "%s.TE_assigned" % experiment)
    cmd4 = "python counts2mtx.py %s %s %s %s" % (barcode_file, summary_file, file_in, file_out)
    #return (cmd1, cmd2, cmd3, cmd4)
    return cmd3


def main():
    cmds = []
    for experiment in get_experiment(home, project):
        path = os.path.join(home, "data", project, experiment)
        cmd = umi_counts(path, experiment)
        cmds.append(cmd)
    exe_parallel(cmds, threads)


if __name__ == '__main__':
    main()
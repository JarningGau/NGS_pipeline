from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
threads = int(sys.argv[3])

def bam_group(path, experiment):
    bam_in = os.path.join(path, "%s.gene_assigned.dedup.sorted.bam" % experiment)
    group_out = os.path.join(path, "%s.gene.dedup.group.tsv" % experiment)
    bam_out = os.path.join(path, "%s.gene_assigned.dedup.sorted.group.bam" % experiment)
    logfile = os.path.join(path, "%s.gene_assigned.dedup.sorted.group.log" % experiment)
    cmd1 = '''umi_tools group \
-I %s \
--group-out=%s \
--output-bam \
-S %s \
--log %s \
--gene-tag=XT --assigned-status-tag=XS \
--per-gene --per-cell''' % (bam_in, group_out, bam_out, logfile)
    bam_in = os.path.join(path, "%s.TE_assigned.dedup.sorted.bam" % experiment)
    group_out = os.path.join(path, "%s.TE.dedup.group.tsv" % experiment)
    bam_out = os.path.join(path, "%s.TE_assigned.dedup.sorted.group.bam" % experiment)
    logfile = os.path.join(path, "%s.TE_assigned.dedup.sorted.group.log" % experiment)
    cmd2 = '''umi_tools group \
-I %s \
--group-out=%s \
--output-bam \
-S %s \
--log %s \
--gene-tag=XT --assigned-status-tag=XS \
--per-gene --per-cell''' % (bam_in, group_out, bam_out, logfile)
    return (cmd1, cmd2)

def main():
    cmds = []
    for experiment in get_experiment(home, project):
        path = os.path.join(home, "data", project, experiment)
        cmd = bam_group(path, experiment)
        cmds.append(cmd)
    exe_parallel(cmds, threads)


if __name__ == '__main__':
    main()
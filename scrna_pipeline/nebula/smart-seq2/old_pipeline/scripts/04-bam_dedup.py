from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
threads = int(sys.argv[3])

def bam_dedup(bam_in, bam_out, logfile, out_stat):
    cmd1 = "time samtools index %s" % bam_in
    cmd2 = '''time umi_tools dedup \
--stdin=%s \
--output-stats=%s \
--log=%s \
--per-cell \
> %s''' % (bam_in, out_stat, logfile, bam_out)
    return (cmd1, cmd2)

def main():
    cmds = []
    for experiment in get_experiment(home, project):
        path = os.path.join(home, "data", project, experiment)
        bam_in = os.path.join(path, get_files(path, "Aligned.sortedByCoord.out.bam")[0])
        bam_out = os.path.join(path, "%s.Aligned.sortedByCoord.out.dedup.bam" % experiment)
        logfile = os.path.join(path, "%s.Aligned.sortedByCoord.out.dedup.log" % experiment)
        out_stat = os.path.join(path, experiment)
        cmd = bam_dedup(bam_in, bam_out, logfile, out_stat)
        cmds.append(cmd)
    exe_parallel(cmds, threads)


if __name__ == '__main__':
    main()
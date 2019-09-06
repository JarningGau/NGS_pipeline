from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
gene_gtf = sys.argv[3]
TE_gtf = sys.argv[4]
threads = int(sys.argv[5]) # cpu per cmd
batch_size = int(sys.argv[6])


def reads_assign_on_gene(path, summary, bam_in, experiment):
    cmd0 = 'echo "processing %s"\ncd %s' % (experiment, path)
    cmd1 = '''time featureCounts \
-a %s \
--extraAttributes gene_id,gene_name,gene_type \
-T %s \
-o %s \
-R BAM %s''' % (gene_gtf, threads, summary, bam_in)
    cmd2 = "rm %s.featureCounts.bam" % bam_in
    # cmd2 = "mv %s.featureCounts.bam %s.gene_assigned.dedup.bam" % (bam_in, experiment)
    # cmd3 = "time samtools sort -@ 24 %s.gene_assigned.dedup.bam -o %s.gene_assigned.dedup.sorted.bam" % (
    #     experiment, experiment)
    # cmd4 = "time samtools index %s.gene_assigned.dedup.sorted.bam" % (experiment)
    # return (cmd0, cmd1, cmd2, cmd3, cmd4)
    return (cmd0, cmd1, cmd2)


def reads_assign_on_TE(path, summary, bam_in, experiment):
    cmd0 = "cd %s" % path
    cmd1 = '''time featureCounts \
-a %s \
--extraAttributes gene_id,family_id,class_id \
-T %s \
-o %s \
-R BAM %s''' % (TE_gtf, threads, summary, bam_in)
    cmd2 = "mv %s.featureCounts.bam %s.TE_assigned.dedup.bam" % (bam_in, experiment)
    cmd3 = "time samtools sort -@ 24 %s.TE_assigned.dedup.bam -o %s.TE_assigned.dedup.sorted.bam" % (
        experiment, experiment)
    cmd4 = "time samtools index %s.TE_assigned.dedup.sorted.bam" % (experiment)
    return (cmd0, cmd1, cmd2, cmd3, cmd4)


def main():
    cmds = []
    for experiment in get_experiment(home, project):
        path = os.path.join(home, "data", project, experiment)
        bam_in = "%s.Aligned.sortedByCoord.out.dedup.bam" % experiment
        summary_gene = "%s.gene_assigned" % experiment
        summary_te = "%s.TE_assigned" % experiment
        cmd_tuple = reads_assign_on_gene(path, summary_gene, bam_in, experiment)
        cmds.append(cmd_tuple)
        # cmd_tuple = reads_assign_on_TE(path, summary_te, bam_in, experiment)
        # cmds.append(cmd_tuple)
    cmd_list = make_parallel(cmds, batch_size)
    for i in range(len(cmd_list)):
        fo = open(os.path.join(home, "05-assignment-%s.pbs" %(i+1)), 'w')
        fo.write('''#!/bin/sh
#PBS -N preprocess_s5-b%s
#PBS -o preprocess_s5-b%s.log
#PBS -e preprocess_s5-b%s.err
#PBS -q middle
#PBS -l nodes=1:ppn=%s
#PBS -l mem=10G

module load samtools
module load Anaconda3

cd %s
echo "step5 Reads assignment, processing batch-%s"\n
''' % (i+1, i+1, i+1, threads, home, i+1))
        for cmd_tuple in cmd_list[i]:
            for cmd in cmd_tuple:
                fo.write(cmd+"\n")
            fo.write("\n\n")
        fo.close()


if __name__ == '__main__':
    main()
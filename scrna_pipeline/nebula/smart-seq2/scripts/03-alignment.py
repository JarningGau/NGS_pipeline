from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
reference = sys.argv[3]
threads = int(sys.argv[4]) # cpu per cmd
batch_size = int(sys.argv[5])


def starAlignment(fq, out_prefix):
    cmd = '''STAR --runThreadN %s \
--genomeDir %s \
--readFilesIn %s \
--readFilesCommand zcat \
--outFilterMultimapNmax 50 \
--winAnchorMultimapNmax 50 \
--outSAMtype BAM SortedByCoordinate \
--outFileNamePrefix %s ''' %(threads, reference, fq, out_prefix)
    return cmd

def main():
    cmds = []
    for experiment in get_experiment(home, project):
        path = os.path.join(home, "data", project, experiment)
        fq1 = os.path.join(path, "%s_R1.clean.extracted_trimTSO_trimPolyA.fastq.gz" % experiment)
        out_prefix = os.path.join(path, "%s." % experiment)
        cmd = starAlignment(fq1, out_prefix)
        cmds.append(cmd)
    cmd_list = make_parallel(cmds, batch_size)
    for i in range(len(cmd_list)):
        fo = open(os.path.join(home, "03-alignment-%s.pbs" %(i+1)), 'w')
        fo.write('''#!/bin/sh
#PBS -N preprocess_s3-b%s
#PBS -o preprocess_s3-b%s.log
#PBS -e preprocess_s3-b%s.err
#PBS -q middle
#PBS -l nodes=1:ppn=%s
#PBS -l mem=10G

module load STAR

cd %s
echo "step3 STAR alignment, processing batch-%s"\n
''' % (i+1, i+1, i+1, threads, home, i+1))
        for cmd in cmd_list[i]:
            fo.write(cmd)
            fo.write("\n\n")
        fo.close()


if __name__ == '__main__':
    main()

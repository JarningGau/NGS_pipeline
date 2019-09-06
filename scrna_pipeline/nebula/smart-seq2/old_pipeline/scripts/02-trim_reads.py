from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
tso_fa = sys.argv[3]
polyA_fa = sys.argv[4]
threads = int(sys.argv[5]) # cpu per cmd
batch_size = int(sys.argv[6])


def trimTSO(fq, out_prefix):
	cmd = '''time flexbar --adapter-min-overlap 7 --adapter-trim-end LEFT --adapters %s \
--min-read-length 16 --threads %s \
--reads %s \
--target %s''' % (tso_fa, threads, fq, out_prefix)
	return cmd

def trimPolyA(fq, out_prefix):
	cmd = '''time flexbar --adapter-min-overlap 7 --adapter-trim-end RIGHT --adapters %s \
--min-read-length 16 --threads %s \
--reads %s \
--target %s -z GZ''' % (polyA_fa, threads, fq, out_prefix)
	return cmd

def main():
	cmds = []
	for experiment in get_experiment(home, project):
		path = os.path.join(home, "data", project, experiment)
		fq1 = os.path.join(path, "%s_R1.clean.extracted.fq.gz" % experiment)
		out_prefix1 = os.path.join(path, "%s_R1.clean.extracted_trimTSO" % experiment)
		fq2 = os.path.join(path, "%s_R1.clean.extracted_trimTSO.fastq" % experiment)

		out_prefix2 = os.path.join(path, "%s_R1.clean.extracted_trimTSO_trimPolyA" % experiment)
		cmd1 = trimTSO(fq1, out_prefix1)
		cmd2 = trimPolyA(fq2, out_prefix2)
		cmd3 = "rm %s" % fq2
		cmd = (cmd1, cmd2, cmd3)
		cmds.append(cmd)
	cmd_list = make_parallel(cmds, batch_size)
	for i in range(len(cmd_list)):
		fo = open(os.path.join(home, "02-trim_reads-%s.pbs" %(i+1)), 'w')
		fo.write('''#!/bin/sh
#PBS -N preprocess_s2-b%s
#PBS -o preprocess_s2-b%s.log
#PBS -e preprocess_s2-b%s.err
#PBS -q low
#PBS -l nodes=1:ppn=%s
#PBS -l mem=10G

module load flexbar

cd %s
echo "step2 Trim reads on R1, processing batch-%s"\n
''' % (i+1, i+1, i+1, threads, home, i+1))
		for cmd_tuple in cmd_list[i]:
			for cmd in cmd_tuple:
				fo.write(cmd)
				fo.write("\n")
			fo.write("\n\n")
		fo.close()


if __name__ == '__main__':
	main()
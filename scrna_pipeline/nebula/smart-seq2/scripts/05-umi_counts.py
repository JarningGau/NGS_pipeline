from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
threads = int(sys.argv[3])


def umi_count(bam, count_file):
	cmd = '''umi_tools count --per-gene --gene-tag=XT \
--assigned-status-tag=XS \
--per-cell \
-I %s \
-S %s
	''' % (bam, count_file)
	return cmd


def main():
	cmds = []
	for experiment in get_experiment(home, project):
		path = os.path.join(home, "data", project, experiment)
		bam_gene = os.path.join(path, "%s.gene_assigned.sorted.bam" % experiment)
		bam_TE = os.path.join(path, "%s.TE_assigned.sorted.bam" % experiment)
		count_file_gene = os.path.join(path, "%s.gene_counts.tsv.gz" % experiment)
		count_file_TE = os.path.join(path, "%s.TE_counts.tsv.gz" % experiment)
		cmd1 = umi_count(bam_gene, count_file_gene)
		cmd2 = umi_count(bam_TE, count_file_TE)
		cmds.append(cmd1)
		cmds.append(cmd2)
	exe_parallel(cmds, threads)


if __name__ == '__main__':
	main()
from parallel import *
from utils import *
import sys


home = sys.argv[1]
project = sys.argv[2]
barcode_file = sys.argv[3]
threads = int(sys.argv[4])


def umi_tools_extract(fq1, fq2, fq1_out, fq2_out, logfile):
	cmd = '''umi_tools extract --bc-pattern CCCCCCCCNNNNNNNN \
--stdin %s \
--stdout %s \
--read2-in %s \
--read2-out %s \
--filter-cell-barcode \
-L %s
--whitelist %s
	''' % (fq2, fq2_out, fq1, fq1_out, logfile, barcode_file)
	return cmd


def main():
	cmds = []
	for experiment in get_experiment(home, project):
		path = os.path.join(home, "data", project, experiment)
		fq1 = os.path.join(path, get_files(path, "R1.clean.fq.gz")[0])
		fq2 = os.path.join(path, get_files(path, "R2.clean.fq.gz")[0])
		fq1_out = os.path.join(path, "%s_R1.clean.extracted.fq.gz" % experiment)
		fq2_out = os.path.join(path, "%s_R2.clean.extracted.fq.gz" % experiment)
		logfile = os.path.join(path, "%s.extract.log" % experiment)
		cmd = umi_tools_extract(fq1, fq2, fq1_out, fq2_out, logfile)
		cmds.append(cmd)
	exe_parallel(cmds, threads)


if __name__ == '__main__':
	main()
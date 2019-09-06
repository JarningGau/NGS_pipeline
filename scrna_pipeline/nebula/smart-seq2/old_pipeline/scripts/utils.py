import os


def get_files(path, appendix):
    return sorted([f for f in os.listdir(path) if f.endswith(appendix)])


def get_experiment(home, project):
	path = os.path.join(home, "data", project)
	return sorted(os.listdir(path))
import os
import collections

from . import core


class LongPathFinderParams:
    def __init__(self):
        self.root_dir = None
        self.limit = None
        self.log_file = None


class LongPathFinder:
    def __init__(self, logger=core.container.logger()):
        self.params = None
        self.logger = logger

    def find(self, params):
        self.params = params

        long_names = find_long_file_names(self.params.root_dir, int(self.params.limit))
        for directory, files in long_names.items():
            self.logger.info(f"Directory: {directory}")
            for file in files:
                if self.params.log_file:
                    self.logger.info(f" - {file}")


def find_long_file_names(root_directory, max_length=260):
    long_names = collections.defaultdict(list)
    for root, directories, files in os.walk(root_directory):
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))
            if len(file_path) > max_length:
                long_names[root].append(file)
    return long_names


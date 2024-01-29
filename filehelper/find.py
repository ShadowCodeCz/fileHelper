import os
import re
import datetime

from . import core


class FileFinderParams:
    def __init__(self):
        self.root_dir = None
        self.regular_expression = None
        self.output = None
        self.verbose = None


class FilesFinder:
    def __init__(self, logger=core.container.logger()):
        self.params = None
        self.logger = logger

    def find(self, params):
        self.params = params

        files = find_files(self.params.root_dir, self.params.regular_expression)
        files_objects = list(map(core.File, files))

        dt = datetime.datetime.now()
        output_path = dt.strftime(self.params.output)

        content = {fo.path: fo.to_dict() for fo in files_objects if os.path.exists(fo.path)}
        core.write_json(output_path, content)

        if self.params.verbose:
            for fo in files_objects:
                self.logger.info(fo.path)

        self.logger.info(f"{output_path}: {len(files_objects)}")


def find_files(root_dir, regular_expression):
    result = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            if abs_path not in result and re.search(regular_expression, abs_path):
                result.append(abs_path)
    return result


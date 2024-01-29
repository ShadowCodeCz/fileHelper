import os
import datetime

from . import core


class HashComputerParams:
    def __init__(self):
        self.files_path = None
        self.suppress_sha256 = None
        self.suppress_md5 = None
        self.save_limit = None
        self.output = None


class HashComputer:
    def __init__(self, logger=core.container.logger()):
        self.params = None
        self.logger = logger

    def compute(self, params):
        self.params = params

        files = core.read_json(self.params.files_path)

        i = 0
        y = 0
        save_limit = int(self.params.save_limit)
        not_computed_files = {k: v for k, v in files.items() if "size" not in v}
        count_not_computed_files = len(not_computed_files)

        dt = datetime.datetime.now()
        output_path = dt.strftime(self.params.output)

        for path_key in not_computed_files:
            y += 1

            if not os.path.exists(path_key):
                self.logger.warn(f"The path '{path_key}' does not exists.")
                del files[path_key]
                continue

            files[path_key] = {
                "path": path_key,
                "size": core.FileOperation.get_size(core.fix_path(path_key)),
                "hash": core.FileOperation.compute_hashes(
                    core.fix_path(path_key),
                    not self.params.suppress_sha256,
                    not self.params.suppress_md5
                )
            }
            i += 1

            if i > save_limit:
                i = 0
                core.write_json(output_path, files)
                self.logger.info(f"Processed {y} of {count_not_computed_files}")

        core.write_json(output_path, files)
        self.logger.info(f"Processed {y} of {count_not_computed_files}")
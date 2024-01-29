import json
import os.path

from . import core


class ComparatorParams:
    def __init__(self):
        self.left_hash_file_path = None
        self.right_hash_file_path = None
        self.use_filename = None
        self.use_size = None
        self.use_md5 = None
        self.use_sha256 = None
        self.log_match = None
        self.log_signature = None


class Comparator:
    def __init__(self, logger=core.container.logger()):
        self.params = None
        self.logger = logger

    def compare(self, params):
        self.params = params
        left = self.read_json(self.params.left_hash_file_path)
        right = self.read_json(self.params.right_hash_file_path)
        self.compare_one_side(left, right)
        self.compare_one_side(right, left)

    def compare_one_side(self, first, second):
        matched = False
        matched_key = ""
        for first_key, first_item in first.items():
            first_sig = self.signature(first_item)
            matched = False

            for second_key, second_item in second.items():
                matched_key = second_key
                second_sig = self.signature(second_item)
                if second_sig == first_sig:
                    matched = True
                    break

            if not matched:
                if self.params.log_signature:
                    self.logger.info(f"< NOT > {first_key} NOT matched [{first_sig}]")
                else:
                    self.logger.info(f"< NOT > {first_key} NOT matched")
            else:
                if self.params.log_match:
                    if self.params.log_signature:
                        self.logger.info(f"{first_key} < ---- > {matched_key} [{first_sig}]")
                    else:
                        self.logger.info(f"{first_key} < ---- > {matched_key}")

    def read_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def signature(self, item):
        sig = ""
        if self.params.use_filename:
            sig += os.path.basename(self.read_path(item))
        if self.params.use_size:
            sig += str(self.read_size(item))
        if self.params.use_md5:
            sig += self.read_md5(item)
        if self.params.use_sha256:
            sig += self.read_sha256(item)
        return sig

    def read_path(self, item):
        try:
            return item["path"]
        except Exception as e:
            self.logger.warn(f"Attribute path does not exists: {item}")
            return ""

    def read_size(self, item):
        try:
            return item["size"]
        except Exception as e:
            self.logger.warn(f"Attribute size does not exists: {item}")
            return ""

    def read_md5(self, item):
        try:
            return item["hash"]["md5"]
        except Exception as e:
            self.logger.warn(f"Attribute md5 does not exists: {item}")
            return ""

    def read_sha256(self, item):
        try:
            return item["hash"]["sha256"]
        except Exception as e:
            self.logger.warn(f"Attribute sha256 does not exists: {item}")
            return ""
import hashlib
import json
import logging.config
import os
import apphelpers as app_helpers


from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    app_description = providers.Singleton(app_helpers.AppDescription, "file.helper")
    locale_paths = providers.Singleton(app_helpers.LocalePaths, app_description)
    package_paths = providers.Singleton(app_helpers.PackagePaths, app_description(), os.path.dirname(__file__))
    logger_helper = providers.Singleton(app_helpers.LoggerHelper, app_description, locale_paths)
    logger = providers.Factory(logging.getLogger, name=logger_helper().logger_name())
    help = providers.Singleton(app_helpers.Help, locale_paths, logger)
    locale_cfg_helper = providers.Singleton(app_helpers.Configuration, locale_paths, logger)
    cfg = providers.Configuration()

container = Container()


class FileOperation:
    @staticmethod
    def compute_hashes(path, compute_sha256, compute_md5):
        hashes = {
            "sha256": None,
            "md5": None
        }
        with open(path, 'rb') as file:
            buffer = file.read(65536)  # Read in blocks for efficiency
            sha256_hasher = hashlib.sha256() if compute_sha256 else None
            md5_hasher = hashlib.md5() if compute_md5 else None

            while len(buffer) > 0:
                if sha256_hasher:
                    sha256_hasher.update(buffer)
                if md5_hasher:
                    md5_hasher.update(buffer)
                buffer = file.read(65536)

            if sha256_hasher:
                hashes['sha256'] = sha256_hasher.hexdigest()
            if md5_hasher:
                hashes['md5'] = md5_hasher.hexdigest()

        return hashes

    @staticmethod
    def get_size(path):
        return os.path.getsize(path)


class File:
    def __init__(self, path):
        self.path = path

    def to_dict(self):
        return {"path": self.path}


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, content):
    with open(path, "w+") as f:
        json.dump(content, f, indent=4)


def fix_path(path):
    return path.replace("\\\\", "\\")
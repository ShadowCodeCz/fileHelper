import os.path
import argparse

from . import cli
from . import core


def main():
    logger_helper = core.container.logger_helper()
    logger_helper.prepare_output_directory()
    logger_helper.configure()

    help = core.container.help()
    help.create_empty_help("app")
    help.read()
    app_help_text = help.get_help("app")


    locale_paths = core.container.locale_paths()
    cfg_helper = core.container.locale_cfg_helper()
    cfg_helper.create_cfg("default.sort.rules",
                          {"rule.key": {
                              "variables": {},
                              "re.include": [],
                              "re.exclude": [],
                              "path.template": "./{variable}/dir/%Y.%m.%dT%H.%M.%S"
                          }})

    description = app_help_text

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers()

    # LIST
    list_files_parser = subparsers.add_parser('list', aliases=["ls"])
    list_files_parser.add_argument("-d", "--root-dir", default=".")
    list_files_parser.add_argument("-o", "--output", default="files.%Y.%m.%dT%H.%M.%S.json")
    list_files_parser.add_argument("-e", "--regular-expression", default=".*")
    list_files_parser.add_argument("-v", "--verbose", action='store_true')
    list_files_parser.set_defaults(func=cli.list_command)

    # COMPUTE HASH
    hash_parser = subparsers.add_parser('hash')
    hash_parser.add_argument("-p", "--files-path", required=True)
    hash_parser.add_argument("-o", "--output", default="hashes.%Y.%m.%dT%H.%M.%S.json")
    hash_parser.add_argument("--suppress-md5", action='store_true')
    hash_parser.add_argument("--suppress-sha256", action='store_true')
    hash_parser.add_argument("-s", "--save-limit", default=100)
    hash_parser.set_defaults(func=cli.hash_command)

    # SORT
    # TODO: RESENI KONFLIKTU PRI PRESUNU - (HLEDANI NEKONFLIKTNIHO JMENA)
    # Obrazky VS MOVIE
    # TODO: -v "variables"
    # {"rule.key": {
    #     "variables": {},
    #     "re.include": [],
    #     "re.exclude": [],
    #     "path.template": "./{variable}/dir/%Y.%m.%dT%H.%M.%S"
    # }}
    # sort_parser = subparsers.add_parser('sort')
    # sort_parser.set_defaults(func=cli.sort)

    sort_parser = subparsers.add_parser('sort')
    # sort_parser.add_argument("-i", "--input-root-directory", default=".")
    sort_parser.add_argument("-r", "--rules-cfg-path", default=locale_paths.configuration_file("default.sort.rules"))
    sort_parser.add_argument("-v", "--variables", default=[], nargs='*')
    sort_parser.add_argument("-m", "--mode", default="move", help="move, copy")
    sort_parser.add_argument("-s", "--simulation", action='store_true')
    sort_parser.add_argument("-f", "--first-rule-match-only", action='store_true')
    sort_parser.set_defaults(func=cli.sort_command)


    # COMPARE
    # TODO: Vystup do JSON souboru
    compare_parser = subparsers.add_parser('compare')
    compare_parser.add_argument("-l", "--left-hash-file", required=True)
    compare_parser.add_argument("-r", "--right-hash-file", required=True)
    compare_parser.add_argument("-f", "--use-filename", action='store_true')
    compare_parser.add_argument("-s", "--use-size", action='store_true')
    compare_parser.add_argument("-m", "--use-md5", action='store_true')
    compare_parser.add_argument("-a", "--use-sha256", action='store_true')
    compare_parser.add_argument("-g", "--log-match", action='store_true')
    compare_parser.add_argument("-u", "--log-signature", action='store_true')
    compare_parser.set_defaults(func=cli.compare_command)

    # FIND DUPLICIT FILES
    # add-filename
    # add-size
    # add-md5
    # add-sha256

    # FIND LONG PATH
    long_parser = subparsers.add_parser('long')
    long_parser.add_argument("-d", "--root-dir", default=".")
    long_parser.add_argument("-l", "--limit", default=190)
    long_parser.add_argument("-o", "--log-file", action='store_true')
    long_parser.set_defaults(func=cli.long_command)


    # JOIN TWO HASH FILES

    arguments = parser.parse_args()
    arguments.func(arguments)

# TODO: List all files by RE
# TODO: Move files
# TODO: Count hash (md5, )
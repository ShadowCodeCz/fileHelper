from . import compare
from . import find
from . import hash
from . import long
from . import sort


def list_command(arguments):
    params = find.FileFinderParams()
    params.root_dir = arguments.root_dir
    params.regular_expression = arguments.regular_expression
    params.output = arguments.output
    params.verbose = arguments.verbose

    finder = find.FilesFinder()
    finder.find(params)


def hash_command(arguments):
    params = hash.HashComputerParams()
    params.files_path = arguments.files_path
    params.suppress_sha256 = arguments.suppress_sha256
    params.suppress_md5 = arguments.suppress_md5
    params.save_limit = arguments.save_limit
    params.output = arguments.output

    computer = hash.HashComputer()
    computer.compute(params)


def sort_command(arguments):
    params = sort.SorterParams()
    # params.input_root_directory = arguments.input_root_directory
    params.rules_cfg_path = arguments.rules_cfg_path
    params.variables = sort.parse_cli_variables(arguments.variables)
    params.mode = arguments.mode.strip()
    params.simulation = arguments.simulation
    params.first_rule_match_only = arguments.first_rule_match_only

    sorter = sort.Sorter()
    sorter.sort(params)


def compare_command(arguments):
    params = compare.ComparatorParams()
    params.left_hash_file_path = arguments.left_hash_file
    params.right_hash_file_path = arguments.right_hash_file
    params.use_filename = arguments.use_filename
    params.use_size = arguments.use_size
    params.use_md5 = arguments.use_md5
    params.use_sha256 = arguments.use_sha256
    params.log_match = arguments.log_match
    params.log_signature = arguments.log_signature

    comparator = compare.Comparator()
    comparator.compare(params)


def long_command(arguments):
    params = long.LongPathFinderParams()
    params.root_dir = arguments.root_dir
    params.limit = int(arguments.limit)
    params.log_file = arguments.log_file

    finder = long.LongPathFinder()
    finder.find(params)




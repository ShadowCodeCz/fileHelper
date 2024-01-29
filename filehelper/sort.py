import datetime
import os.path
import re
import shutil
import traceback

from . import core
import alphabetic_timestamp as ats


def parse_cli_variables(raw):
    pairs = raw

    result = {}
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split("=", 1)
            if key and value:
                result[key] = value
    return result

def parse_cli_variables_as_one_string(raw):
    pairs = re.split(r'[;,]', raw)

    result = {}
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split("=", 1)
            if key and value:
                result[key] = value
    return result


class SorterParams:
    def __init__(self):
        # self.input_root_directory = None
        self.rules_cfg_path = None
        self.variables = None
        self.mode = None
        self.simulation = None
        self.first_rule_match_only = None


class Sorter:
    def __init__(self, logger=core.container.logger()):
        self.params = None
        self.logger = logger

        self.rule_parser = RuleParser()
        self.files_finder = FilesFinder()
        self.matcher = Matcher()
        self.copy_executor = CopyExecutor()
        self.move_executor = MoveExecutor()

    def sort(self, params):
        self.params = params

        rules = self.parse_rules()

        for file in self.list_files():
            try:
                matches = self.matcher.match(file, rules, params)
                if len(matches) > 0:
                    self.execute(matches)
            except Exception as e:
                self.logger.error(traceback.format_exc())
                self.logger.error(f"Error during processing {file}.{e}")

    def read_rules(self):
        return core.read_json(self.params.rules_cfg_path)

    def parse_rules(self):
        return self.rule_parser.parse(self.read_rules())

    def list_files(self):
        return self.files_finder.find(".")

    def execute(self, matches):
        mode = self.params.mode

        for match in matches:
            if mode == "copy":
                self.copy_executor.execute(match, self.params)
            if mode == "move":
                self.move_executor.execute(match, self.params)


class Rule:
    def __init__(self):
        self.variables = {}
        self.re_included = []
        self.re_excluded = []
        self.path_template = ""


class RuleParser:
    def __init__(self, logger=core.container.logger()):
        self.logger = logger

    def parse(self, json_dict):
        rules = []
        for rule_name, json_rule in json_dict.items():
            r = Rule()
            r.variables = self.parse_variables(json_rule)
            r.re_included = self.parse_re_included(json_rule)
            r.re_excluded = self.parse_re_excluded(json_rule)
            r.path_template = self.parse_path_template(json_rule)
            rules.append(r)
        return rules

    def parse_variables(self, json_rule):
        if "variables" not in json_rule:
            return {}
        else:
            return json_rule["variables"]

    def parse_re_included(self, json_rule):
        if "re.include" not in json_rule:
            return [".*"]
        else:
            return json_rule["re.include"]

    def parse_re_excluded(self, json_rule):
        if "re.exclude" not in json_rule:
            return []
        else:
            return json_rule["re.exclude"]

    def parse_path_template(self, json_rule):
        return json_rule["path.template"]


class FilesFinder:
    def find(self, directory="."):
        return self.get_all_files(directory)

    def get_all_files(self, directory):
        all_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                all_files.append(os.path.join(root, file))
        return all_files


class MatchSingleFileResult:
    def __init__(self, file, included_matches, rule):
        self.file = file
        self.included_matches = included_matches
        self.rule = rule


class Matcher:
    def __init__(self, logger=core.container.logger()):
        self.logger = logger
        self.rules = None

    def match(self, file, rules, params):
        result = []
        for rule in rules:
            included_matches = self.match_single_group_re(file, rule.re_included)
            if len(included_matches) > 0:
                excluded_matches = self.match_single_group_re(file, rule.re_excluded)

                if len(excluded_matches) == 0:
                    m = MatchSingleFileResult(file, included_matches, rule)
                    result.append(m)

                    if params.first_rule_match_only:
                        continue

        return result

    def match_single_group_re(self, file, re_expressions_group):
        result = []
        for expression in re_expressions_group:
            m = re.search(expression, file)
            if m:
                result.append(m)
        if len(result) > 0:
            self.logger.debug(f"match_single_group_re({file}, {str(re_expressions_group)}): {str(result)}")
        return result


class VariablesBuilder:
    def __init__(self, dt):
        self.now = dt
        self.static_ats = ats.base62.from_datetime(dt, time_unit=ats.TimeUnit.milliseconds)

    def build(self, file_match, global_variables):
        result = {**self.predefined(file_match), **global_variables, **file_match.rule.variables}
        for m in file_match.included_matches:
            if m:
                result.update(m.groupdict())
        return result

    def predefined(self, file_match):
        return {
            "predefined.static.ats": str(self.static_ats),
            "predefined.static.now.year": str(self.now.year),
            "predefined.static.now.day": str(self.now.day),
            "predefined.static.now.hour": str(self.now.hour),
            "predefined.dynamic.ats": str(ats.base62.now(time_unit=ats.TimeUnit.milliseconds)),
            "predefined.original.filename": str(os.path.basename(file_match.file)),
            "predefined.original.path": file_match.file,
            "predefined.original.path.without.first.char": str(file_match.file[1:])
        }


class PathEvaluator:
    def __init__(self, dt, logger=core.container.logger()):
        self.logger = logger
        self.dt = dt

    def evaluate(self, path_template, variables):
        return self.dt.strftime(self.replace_variables(path_template, variables))

    def replace_variables(self, path_template, variables):
        def replace_match(match):
            key = match.group(1)
            default_key = f"default.{key}"

            if key in variables:
                return variables[key]
            elif default_key in variables:
                return variables[default_key]
            else:
                raise ValueError(f"Key '{key}' nether key '{default_key}' do not exist. Keys were used in template {path_template}")

        return re.sub(r'\{([^\}]+)\}', replace_match, path_template)


class Executor:
    def __init__(self, logger=core.container.logger()):
        self.logger = logger
        self.params = None
        self.match = None
        self.dt = datetime.datetime.now()
        self.variables_builder = VariablesBuilder(self.dt)
        self.path_evaluator = PathEvaluator(self.dt)

    def execute(self, match, params):
        # TODO: IF EXISTS
        # TODO: NOT EXISTS DIRECTORIES
        self.match = match
        self.params = params
        self.specific_execution()

    def specific_execution(self):
        pass

    def source(self):
        return os.path.normpath(self.match.file)

    def destination(self):
        variables = self.variables_builder.build(self.match, self.params.variables)
        dst = self.path_evaluator.evaluate(self.match.rule.path_template, variables)
        return os.path.normpath(self.non_conflicting_destination(dst))

    def non_conflicting_destination(self, path):
        directory, filename = os.path.split(path)
        filename_without_suffix, suffix = os.path.splitext(filename)

        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{filename_without_suffix}.cp{counter}{suffix}"
            counter += 1

        return os.path.join(directory, new_filename)

    def should_execute(self):
        return not self.params.simulation and os.path.exists(self.source())

    def simulation_text(self):
        return " [sim]" if self.params.simulation else ""

    def get_directory_path(self, path):
        if os.path.isdir(path) and (path.endswith("/") or path.endswith("\\")):
            return path
        else:
            return os.path.dirname(path) + os.sep

class CopyExecutor(Executor):
    def specific_execution(self):
        self.logger.info(f"COPY{self.simulation_text()}: {self.source()} ---> {self.destination()}")
        if self.should_execute():
            os.makedirs(self.get_directory_path(self.destination()), exist_ok=True)
            shutil.copy(self.source(), self.destination())


class MoveExecutor(Executor):
    def specific_execution(self):
        self.logger.info(f"MOVE{self.simulation_text()}: {self.source()} ---> {self.destination()}")
        if self.should_execute():
            os.makedirs(self.get_directory_path(self.destination()), exist_ok=True)
            shutil.move(self.source(), self.destination())
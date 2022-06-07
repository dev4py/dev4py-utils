#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022 the original author or authors (i.e.: St4rG00se for Dev4py).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from io import TextIOWrapper
from os import environ as os_environ, pathsep as os_pathsep, getcwd as os_getcwd
from pathlib import Path
from subprocess import run as subprocess_run, CalledProcessError
from sys import argv as sys_argv, stderr as sys_stderr, stdin as sys_stdin, stdout as sys_stdout, exit as sys_exit
from textwrap import dedent
from typing import Final, TypeVar, Any

try:
    try:
        from tomli import loads as tomli_loads
    except ImportError:
        # noinspection PyProtectedMember
        # noinspection PyPackageRequirements
        # noinspection PyUnresolvedReferences
        from pip._vendor.tomli import loads as tomli_loads
except ImportError:
    print(
        "tomli is required (install pip or run this script from poetry venv after `poetry install --no-root` or "
        "`poetry update`)",
        file=sys_stderr)
    sys_exit(1)

# CONSTANTS
# - project
PROJECT_PATH: Final[Path] = Path(__file__).parent.absolute()

# - pyproject file consts
PROJECT_TOML_FILE_PATH: Final[str] = PROJECT_PATH.joinpath('pyproject.toml').as_posix()
PROJECT_SECTION: Final[str] = 'tool.poetry'
STRUCTURE_OPTION: Final[str] = 'packages'

# - sources / test default paths
DEFAULT_DIST_PATH: Final[str] = 'dist'
DEFAULT_BUILD_PATH: Final[str] = 'build'


# CLASSES
# - Project Configuration class
class ProjectProperties:
    T = TypeVar('T')

    def __init__(
            self,
            project_path: Path = PROJECT_PATH,
            toml_file_path: str = PROJECT_TOML_FILE_PATH,
            project_section: str = PROJECT_SECTION,
            structure_option: str = STRUCTURE_OPTION,
            dist_path: str = DEFAULT_DIST_PATH,
            build_path: str = DEFAULT_BUILD_PATH
    ):
        self.__toml_file_path: Final[str] = toml_file_path
        self.__project_section: Final[str] = project_section
        self.__structure_option: Final[str] = structure_option
        self.__toml_file_content: Final[dict[str, Any]] = self._load_toml()

        # - Global
        self.project_path: Final[Path] = project_path
        self.dist_path: Final[str] = dist_path
        self.build_path: Final[str] = build_path
        self.src_rsrc_paths: Final[list[str]] = self._get_sources_and_resources_paths()

    def _load_toml(self) -> dict[str, Any]:
        with open(self.__toml_file_path, "r", encoding="UTF-8") as toml_file:
            return tomli_loads(toml_file.read())

    def _get_option(self, section: str, option: str, default: T | None = None) -> T | None:
        option_path: list[str] = section.split('.')
        path_dict: Any = self.__toml_file_content
        for path in option_path:
            path_dict = path_dict.get(path)
            if not (path_dict and isinstance(path_dict, dict)):
                return default
        return path_dict.get(option, default)

    def _get_sources_and_resources_paths(self) -> list[str]:
        return [
            self.project_path.joinpath(pkg_cnf['from']).as_posix()
            for pkg_cnf in self._get_option(self.__project_section, self.__structure_option, default=[])
            if 'from' in pkg_cnf
        ]


# - Project commands abstract class
class ProjectCommand:
    """The ProjectCommand abstract class used to execute a new project command"""

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def get_command_cwd(self, properties: ProjectProperties) -> str:
        """
        Define the command cwd (by default it is the project path)
        :param properties: the project properties
        :return: the command line cwd
        """
        return properties.project_path.as_posix()

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        """
        Build the command line to execute
        :param properties: the project properties
        :param args: the given argument list to use. Parse it with an ArgumentParser if necessary
        :return: the command argv list (ie sys.argv)
        """
        raise RuntimeError(f"abstract method -- subclass {self.__class__} must override")

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def finalize(self, properties: ProjectProperties) -> None:
        """
        Called once the command is executed in order to clean specific states
        :param properties: the project properties
        """


# -- Poetry Command (used as superclass)
class PoetryCommand(ProjectCommand):
    """Run poetry"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        command_line: Final[list[str]] = ['poetry']
        if args:
            command_line.extend(args)
        return command_line


# -- Load dependencies Command
class LoadDepsCommand(PoetryCommand):
    """Install all dependencies (dev included)"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['install', '--no-root']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Clean Command
class CleanCommand(PoetryCommand):
    """Remove directories generated by the "build" commands (like 'sdist' or 'wheel')"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        clean_script: Final[str] = dedent(f"""\
        from shutil import rmtree
        from pathlib import Path

        def rm_if_exists(path: Path) -> None:
            if path.is_dir():
                print(" |- Remove %s directory" % path)
                rmtree(path)
            elif path.is_file():
                print(" |- Remove %s file" % path)
                path.unlink()

        path_to_rm: list[Path] = [
            Path('{properties.dist_path}'),
            Path('{properties.build_path}'),
            Path('html/'),
            Path('.mutmut-cache')
        ]
        path_to_rm.extend(Path('.').rglob('.tox'))
        path_to_rm.extend(Path('.').rglob('.pytest_cache'))
        for path in path_to_rm:
            rm_if_exists(path)
        """)
        extended_args: Final[list[str]] = ['run', 'python', '-c', clean_script]
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Run Command
class RunCommand(PoetryCommand):
    """Run module which can be in the project structure without having to configure the PYTHONPATH"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        # Use a subprocess in order to be in the good cwd in the poetry venv
        # It is useful when you call project.py from an outside directory
        run_script: Final[str] = dedent(f"""\
        from subprocess import run
        from sys import stdin, stdout, stderr, executable
        run(
            [executable, {str(args or '').strip('[]')}],
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            check=True,
            cwd="{os_getcwd()}")
        """)
        extended_args: Final[list[str]] = ['run', 'python', '-c', run_script]
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Tox Command
class ToxCommand(PoetryCommand):
    """Run tox"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['run', 'tox']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Test Command
class TestCommand(ToxCommand):
    """Run configured unit tests"""
    SKIP_ENV_VAR: Final[str] = 'TOX_SKIP_ENV'

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        os_environ[TestCommand.SKIP_ENV_VAR] = 'pylint|mutation|mypy'
        return super().build_command_line(properties, args)

    def finalize(self, properties: ProjectProperties) -> None:
        os_environ.pop(TestCommand.SKIP_ENV_VAR, None)


# -- Lint Command
class LintCommand(ToxCommand):
    """Run linter"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['-e', 'pylint']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Mutation Command
class MutationCommand(ToxCommand):
    """Run mutation tests"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['-e', 'mutation']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Typing check Command
class TypingCheckCommand(ToxCommand):
    """Run typing checker"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['-e', 'mypy']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Wheel Command
class WheelCommand(PoetryCommand):
    """Build Wheel archive"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['build', '--format', 'wheel']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Sdist Command
class SdistCommand(PoetryCommand):
    """Build sdist archive"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['build', '--format', 'sdist']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# -- Upload Command
class UploadCommand(PoetryCommand):
    """Upload available deliveries"""

    def build_command_line(self, properties: ProjectProperties, args: list[str] | None = None) -> list[str]:
        extended_args: Final[list[str]] = ['publish']
        if args:
            extended_args.extend(args)
        return super().build_command_line(properties, extended_args)


# - Project command executor class
TCommandsRunner = TypeVar("TCommandsRunner", bound="CommandsRunner")


class CommandsRunner:
    def __init__(
            self,
            properties: ProjectProperties,
            stdin: TextIOWrapper = sys_stdin,
            stdout: TextIOWrapper = sys_stdout,
            stderr: TextIOWrapper = sys_stderr
    ):
        self.__project_properties: Final[ProjectProperties] = properties
        self.__stdin: Final[TextIOWrapper] = stdin
        self.__stdout: Final[TextIOWrapper] = stdout
        self.__stderr: Final[TextIOWrapper] = stderr
        self.__command_dict: Final[dict[str, ProjectCommand]] = {}

    def add_command(self, cmd_name: str, cmd: ProjectCommand) -> TCommandsRunner:
        self.__command_dict[cmd_name] = cmd
        return self

    def run(self) -> None:
        if sys_argv and len(sys_argv) > 1:
            argv: str = sys_argv[1]
            if argv in ("--help", "-h"):
                print(self._get_help_str(), file=self.__stdout)
                return

            current_cmd: ProjectCommand | None = self.__command_dict.get(argv)
            if not self.__command_dict.get(argv):
                print(f"Command unknown: '{argv}'", file=self.__stderr)
                return

            current_args: list[str] = []
            for argv in sys_argv[2:]:
                cmd: ProjectCommand | None = self.__command_dict.get(argv)
                if cmd:
                    self._run_process(current_cmd, current_args)
                    current_args.clear()
                    current_cmd = cmd
                else:
                    current_args.append(argv)
            self._run_process(current_cmd, current_args)
        else:
            print("Project command missing use --help or -h for help", file=self.__stderr)

    def _run_process(self, command: ProjectCommand, args: list[str]) -> None:
        try:
            subprocess_run(
                command.build_command_line(self.__project_properties, args),
                stdin=self.__stdin,
                stdout=self.__stdout,
                stderr=self.__stderr,
                check=True,
                cwd=command.get_command_cwd(self.__project_properties)
            )
        except CalledProcessError as e:
            print(f"Command error: [cmd: '{command.__class__.__name__}' | args: '{args}']", file=self.__stderr)
            sys_exit(e.returncode)
        finally:
            command.finalize(self.__project_properties)

    def _get_help_str(self):
        return "PROJECT COMMANDS WRAPPER:\n\n" \
               "Usage: python project.py <COMMAND_1> <arg1_1 ...> ... <COMMAND_N> <argN_1 ...>\n" \
               "\tNote: In order to get the wrapped command help, you can try python project.py <command> --help\n\n" \
               "Available commands are:\n" \
               + ''.join([f"  {cmd}   \t{cls.__doc__}\n" for cmd, cls in self.__command_dict.items()])


# FUNCTIONS
def run(properties: ProjectProperties) -> None:
    """"Execute given commands (from sys.argv) with the configured project structure in the PYTHONPATH"""
    # Configure CommandsRunner
    command_runner: Final[CommandsRunner] = CommandsRunner(properties=properties) \
        .add_command('load_deps', LoadDepsCommand()) \
        .add_command('clean', CleanCommand()) \
        .add_command('run', RunCommand()) \
        .add_command('tox', ToxCommand()) \
        .add_command('lint', LintCommand()) \
        .add_command('test', TestCommand()) \
        .add_command('typing', TypingCheckCommand()) \
        .add_command('mut', MutationCommand()) \
        .add_command('wheel', WheelCommand()) \
        .add_command('sdist', SdistCommand()) \
        .add_command('upload', UploadCommand())

    # Prepare PYTHONPATH
    project_paths: Final[list[str]] = properties.src_rsrc_paths
    pythonpath_env_var: Final[str] = 'PYTHONPATH'
    pythonpath: Final[str] = os_environ.get(pythonpath_env_var)
    if pythonpath:
        project_paths.append(pythonpath)

    # Run commands with project structure in the PYTHONPATH
    try:
        os_environ[pythonpath_env_var] = os_pathsep.join(project_paths)
        command_runner.run()
    finally:
        if pythonpath:
            os_environ[pythonpath_env_var] = pythonpath
        else:
            os_environ.pop(pythonpath_env_var, None)


# SHARED VARIABLES
project_properties = ProjectProperties()

# MAIN
if __name__ == '__main__':
    run(project_properties)

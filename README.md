# PYMSDL_Template

***PYMSDL<sup>(PYthon Maven Standard Directory Layout)</sup> template*** is a
Python [Poetry](https://python-poetry.org/) template inspired from
the [Maven Standard Directory Layout](https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html)
.

[![ci](https://github.com/dev4py/pymsdl_template/actions/workflows/ci.yml/badge.svg?event=push&branch=main)](https://github.com/dev4py/pymsdl_template/actions/workflows/ci.yml) <br/>
[![Last release](https://github.com/dev4py/pymsdl_template/actions/workflows/on_release.yml/badge.svg)](https://github.com/dev4py/pymsdl_template/actions/workflows/on_release.yml) <br/>
[![Python >= 3.10.1](https://img.shields.io/badge/Python->=3.10.1-informational.svg?style=plastic&logo=python)](https://www.python.org/) <br/>
[![Poetry >= 1.1.0](https://img.shields.io/badge/Poetry->=1.1.0-informational.svg?style=plastic&logo=python)](https://python-poetry.org/) <br/>
[![Maintainer](https://img.shields.io/badge/maintainer-St4rG00se-informational?style=plastic&logo=superuser)](https://github.com/St4rG00se) <br/>
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=plastic&logo=github)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity) <br/>
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=plastic&logo=github)](https://opensource.org/licenses/MIT)

**<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/25px-Warning.svg.png" alt="warning-icon" width="20px" height="20px"/>
WARNING Prerequisites:**

* `Python >= 3.10.1`
* `Poetry >= 1.1.0`

***Since there are some existing limitations, it is strongly advised to read
the [Project organization](#project-organization) part before the [Project commands](#project-commands) one.***

> ***Note:** this template is configured in order to work with [Poetry](https://python-poetry.org/).*
>
> *if you want to use another layout than [Maven Standard Directory Layout](https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html),
> you can change the **project structure** as explained in the
> [pyproject.toml & project.py files](#pyprojecttoml--projectpy-files) part.*

## Table of contents

* [Quickstart](#quickstart)
    + [Create a new project](#create-a-new-project)
        - [1. Click on Use this template](#1-click-on-use-this-template)
        - [2. Fork this template](#2-fork-this-template)
        - [3. Clone/download this template](#3-clonedownload-this-template)
    + [Prepare your environment](#prepare-your-environment)
    + [Test your setup](#test-your-setup)
    + [Manage your project](#manage-your-project)
    + [Let's dev](#lets-dev)
* [Project organization](#project-organization)
    + [pyproject.toml & project.py files](#pyprojecttoml--projectpy-files)
    + [Maven Standard Directory Layout with python](#maven-standard-directory-layout-with-python)
        - [Sources & Resources directories configuration](#sources--resources-directories-configuration)
        - [<span style='color: orange'><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/25px-Warning.svg.png" alt="warning-icon" width="20px" height="20px"/> WARNING: Limitations</span>](#-warning-limitations)
            * [A. Use root package names with suffix](#a-use-root-package-names-with-suffix)
            * [B. Use namespace package as root package](#b-use-namespace-package-as-root-package)
            * [C. Don't fully respect the Maven Standard Directory Layout](#c-dont-fully-respect-the-maven-standard-directory-layout)
* [Project commands](#project-commands)
    + [Clean project](#clean-project)
    + [Run module](#run-module)
    + [Run tox](#run-tox)
    + [Run linter](#run-linter)
    + [Run tests](#run-tests)
    + [Run mutation](#run-mutation)
    + [Build](#build)
        - [Wheel archive](#wheel-archive)
        - [Source Distribution](#source-distribution-archive)
    + [Delivery *(on https://pypi.org/)*](#delivery-on-httpspypiorg)
* [Docker](#docker)
    + [Dev environment](#dev-environment)
        - [Build the pymsdl:devenv docker image](#build-the-pymsdldevenv-docker-image)
        - [Run the pymsdl:devenv environment](#run-the-pymsdldevenv-environment)
    + [Docker application image delivery](#docker-application-image-delivery)
        - [Build your docker image](#build-your-docker-image)
        - [Run your docker image](#run-your-docker-image)
        - [Push your docker image](#push-your-docker-image)
* [Workflows](#workflows)
    + [CI](#ci)
    + [On_release](#on_release)

## Quickstart

### Create a new project

There are several ways to use this template for your project:

#### 1. Click on [Use this template](https://github.com/dev4py/pymsdl_template/generate)

Create a new project from the [Use this template](https://github.com/dev4py/pymsdl_template/generate) button is the
standard way for a new GitHub project from a template.

See: [Creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)

> ***Note:** You have to be logged in*

#### 2. Fork this template

Create a new project by forking the template is the "old way" to work with templates on GitHub.

However, there are some differences between "fork" and "use template"
explained [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
which can help you about your choice.

See: [About forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks)

#### 3. Clone/download this template

This is a way to use if you are creating a new project but, you are not working on GitHub.

### Prepare your environment

PYMSDL template requires `Python >= 3.10.1` and `Poetry >= 1.1.0`.

**If your environment is not ready yet, a docker ready to work environment is provided
(see [Dev environment](#dev-environment)).**

In order to simplify your pipeline evolution and local use, this template provides you a python script with basic
management commands. See: [Project commands](#project-commands).

You have to run this command line in order to download your project dependencies:

> ```sh
> ./project.py load_deps
> ```

### Test your setup

PYMSDL template provides a simple sample project named `hellopymsdl`. You can test your setup by running this command
line:

> ```sh
> ./project.py test
> ```

### Manage your project

Since this template use [Poetry](https://python-poetry.org/) you have to learn each
[poetry command](https://python-poetry.org/docs/cli/).

Moreover, this template provides you a python script with basic management commands.
See: [Project commands](#project-commands)

> ***Note** [Project commands](#project-commands) samples should work on the provided `hellopymsdl` simple sample
> project.*

### Let's dev

Once previous steps are done you can start your developments by respecting the content
of [Project organization](#project-organization) part.

## Project organization

### pyproject.toml & project.py files

The [pyproject.toml](./pyproject.toml) file is used in order to describe and deliver correctly your project.

See:

* [PEP 517](https://www.python.org/dev/peps/pep-0517/)
* [PEP 518](https://www.python.org/dev/peps/pep-0518/)
* [PEP 621](https://www.python.org/dev/peps/pep-0621/)
* [PEP 660](https://www.python.org/dev/peps/pep-0660/)
* [Poetry pyproject.toml details](https://python-poetry.org/docs/pyproject/)

Moreover, this template provides the [project.py](./project.py) file which is a command line wrapper in order to
simplify the project evolution (see [Project commands](#project-commands)).

When you start a new project from this template, ***YOU DON'T HAVE TO UPDATE THE [PROJECT.PY](./project.py) FILE***,
until you switch from [Poetry](https://python-poetry.org/) to another tool.

In order to set your project properties, you just have to update the [pyproject.toml](./pyproject.toml).

> **Note:** If you don't want to use the [Maven Standard Directory Layout](https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html),
> you can reconfigure the project structure by replacing each `/src/main/...` or `/src/test/...` by your structure in
> the [pyproject.toml](./pyproject.toml) file.

### Maven Standard Directory Layout with python

#### Sources & Resources directories configuration

This template attempts to reach
the [Maven Standard Directory Layout](https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html)
for python.

That's why you will find the following directory structure:

* ***src/main/python:*** Should contains your application sources
* ***src/main/resources:*** Should contains your application resources
* ***src/test/python:*** Should contains your application **test** sources
* ***src/test/resources:*** Should contains your application  **test** resources

**Sources** and **resources** directories must be in
your **[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH).**

**However, if you don't want to configure your PYTHONPATH, you can use the provided [Run module](#run-module) command.**

> ***Note:** if you are using IDE like **[<img src="https://upload.wikimedia.org/wikipedia/commons/1/1d/PyCharm_Icon.svg" alt="Pycharm-icon" width="17px" height="17px"/>
Pycharm](https://www.jetbrains.com/pycharm/)**
> , it means `src/main/python` and `src/main/resources` must be marked as **Sources Root**
> `(Right click on these directories > Mark directory as > Sources Root)`
> and `src/test/python` and `src/test/resources` must be marked as **Test Sources Root**
> `(Right click on these directories > Mark directory as > Test Sources Root)`.*

> ***Note:** Due to a [Poetry](https://python-poetry.org/) limitation, using  installation with edit mode
> (`pip install -e .`) in order to avoid the
> [PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH) configuration will not work and fail
> with:*
>
> `build backend is missing the 'build_editable' ... Consider using a build backend that supports PEP 660.`

#### <span style='color: orange'><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/25px-Warning.svg.png" alt="warning-icon" width="20px" height="20px"/> WARNING: Limitations</span>

Python resources MUST be located in a python package (ie: directory containing an `__init__.py` file. (You can see that
like a java classpath).

Since a package sources cannot be split in several directories, each package in `src/main/python`,
`src/main/resources`, `src/test/python` and `src/test/resources` directories must be different. In case of conflict, the
package from the first directory found in
your **[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)** will be used.

So if you want to respect the
*[Maven Standard Directory Layout](https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html)*
there are several suggestions:

##### A. Use root package names with suffix

Use root package names with suffixes like this:

* *<My_Root_Package_Name>* for sources (in `src/main/python`)
* *<My_Root_Package_Name>`_rsrc`* for resources (in `src/main/resources`)
* *<My_Root_Package_Name>`_test`* for test sources (in `src/test/python`)
* *<My_Root_Package_Name>`_test_rsrc`* for test resources (in `src/test/resources`)

> **Project structure example:**
>
> ```sh
> <My_Project>
>  |- ...
>  |- src
>      |- main
>      |   |- python
>      |   |   |- <MY_ROOT_PACKAGE_NAME>
>      |   |       |- __init__.py
>      |   |       |- ...
>      |   |- resources
>      |       |- <MY_ROOT_PACKAGE_NAME>_rsrc
>      |           |- __init__.py
>      |           |- ...
>      |- test
>          |- python
>          |   |- <MY_ROOT_PACKAGE_NAME>_test
>          |       |- __init__.py
>          |       |- ...
>          |- resources
>              |- <MY_ROOT_PACKAGE_NAME>_test_rsrc
>                  |- __init__.py
>                  |- ...
> ```

> ***Note:** since root package names are different (`_rsrc`, `_test`, `_test_rsrc` suffixes) it cannot exist conflict
> between packages in `src/main/python`, `src/main/resources`, `src/test/python` and `src/test/resources`.*

> ***Note:** `_rsrc`, `_test`, `_test_rsrc` are just suggested suffixes you can use your own suffixes.*

##### B. Use namespace package as root package

If you really want a common root package name, you can use a `namespace package` as root. This `namespace package` must
contain packages without conflict between sources and resources directories.

> *Reminder: A namespace package doesn't contain any source or `__init__.py` file.*

> **Project structure with namespace package as root package example:**
>
> ```sh
> <My_Project>
>  |- ...
>  |- src
>      |- main
>      |   |- python
>      |   |   |- <MY_ROOT_NAMESPACE_PACKAGE_NAME>
>      |   |       |- <MY_PACKAGE_NAME>
>      |   |       |   |- __init__.py
>      |   |       |   |- ...
>      |   |       |- ...
>      |   |- resources
>      |       |- <MY_ROOT_NAMESPACE_PACKAGE_NAME>
>      |           |- <MY_PACKAGE_NAME>_rsrc
>      |           |   |- __init__.py
>      |           |   |- ...
>      |           |- ...
>      |- test
>          |- python
>          |   |- <MY_ROOT_NAMESPACE_PACKAGE_NAME>
>          |       |- <MY_PACKAGE_NAME>_test
>          |       |   |- __init__.py
>          |       |   |- ...
>          |       |- ...
>          |- resources
>              |- <MY_ROOT_NAMESPACE_PACKAGE_NAME>
>                  |- <MY_PACKAGE_NAME>_test_rsrc
>                  |   |- __init__.py
>                  |   |- ...
>                  |- ...
> ```

##### C. Don't fully respect the Maven Standard Directory Layout

If you are not agree with the previous suggestions, you can remove the `src/main/resources`, `src/test/python`
and `src/test/resources` directories and put your resources and tests directly into the `src/main/python` directory.

> **Note:** if you do that, your tests will be included during your project/package installation (not only in the source
> distribution as it is suggested in the best practices).

## Project commands

Project commands are available from the [project.py](./project.py) python file.

If you take a look at this file, you will see that it contains:

* **A shared `project_properties` variable** which contains all project properties.

* **A command line wrapper:** this wrapper is designed in order to be used locally and in your deployment scripts (like
  CI/CD).

  Indeed, by using it, if you want to update you "project tools" (sample: switching from poetry to setuptools) you just
  have to update this script but not all your pipeline.

  Moreover, this wrapper manage the project [PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)
  for you.

  > **Command wrapper man:**
  > ```sh
  > PROJECT COMMANDS WRAPPER:
  > 
  > Usage: python project.py <COMMAND_1> <arg1_1 ...> ... <COMMAND_N> <argN_1 ...>
  >         Note: In order to get the wrapped command help, you can try python project.py <command> --help
  > 
  > Available commands are:
  >   load_deps     Install all dependencies (dev included)
  >   clean         Remove directories generated by the "build" commands (like 'sdist' or 'wheel')
  >   run           Run module which can be in the project structure without having to configure the PYTHONPATH
  >   tox           Run tox
  >   lint          Run linter
  >   test          Run configured unit tests
  >   mut           Run mutation tests
  >   wheel         Build Wheel archive
  >   sdist         Build sdist archive
  >   upload        Upload available deliveries
  > ```

  > ***Note:** Using `--help` argument on a command or if an error occurs, the message will be from the wrapped command
  > line.*

### Load dependencies

> ```sh
> ./project.py load_deps
> ```
or
> ```sh
> python project.py load_deps
> ```

### Clean project

> ```sh
> ./project.py clean
> ```
or
> ```sh
> python project.py clean
> ```

> ***Note:** Remove dist directory and test cache directories.*

### Run module

PYMSDL template provides you a run python module command line (even in the **project packages**) without having to
configure your **[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)**:

> ```sh
> ./project.py run -m <MODULE_NAME>
> ```
or
> ```sh
> python project.py run -m <MODULE_NAME>
> ```

> ***Note:** the `run` command is like opening python in your poetry virtual environment and the project structure
> configured in your **[PYTHONPATH](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH).***
>
> *Moreover, your opened `python` will work from the current directory (not from the `project.py` one).*

> **Examples:**
>
> **- Open a *python console* from the current directory:**
> ```
> ./project.py run
> ```
> ***Note:** `<PATH_TO_PROJECT.PY> run` will open a python console in your current directory not in the `project.py`
> one.*
>
> **- Run *module* example:**
> ```sh
> ./project.py run -m hellopymsdl.__main__
> ```
> Run the `__main__.py` module from `hellopymsdl` package.
>
> **- Run *package* example:**
> ```sh
> ./project.py run -m hellopymsdl
> ````
> ***Note:** your package MUST contains a `__main__.py` module.*
>
> **- Run *module* from path example:**
> ```sh
> ./project.py run src/main/python/hellopymsdl/__main__.py
> ```
> Run the `__main__.py` module from `hellopymsdl` package.
> **WARNING: the path is from the command `CWD` if not absolute.**
>
> **- Run *package* from path example:**
> ```sh
> ./project.py run src/main/python/hellopymsdl
> ```
> ***Note:** your package MUST contains a `__main__.py` module.*
> **WARNING: the path is from the command `CWD` if not absolute.**
>
> **- Run *module* with arguments example (using --args string parameter):**
> ```sh
> ./project.py run -m hellopymsdl.__main__ --arg1 --arg2=my_arg2 ...
> ```

### Run tox

PYMSDL template uses [tox](https://tox.wiki/) in order to manage your tests (unit tests, lint, etc.)

> ```sh
> ./project.py tox
> ```
or
> ```sh
> python project.py tox
> ```

> ***Note:** You will find the [tox](https://tox.wiki/) configuration in the [pyproject.toml](./pyproject.toml) file
> (`[tool.tox]` section).*
>
> The default [tox](https://tox.wiki/)  configuration provides the following `envlist`:
>
>* ***pylint:*** Executes the configured linter
>* ***covclean:*** Cleans the coverage reports
>* ***py310:*** Executes the configured test runner under python 3.10
>* ***report:*** Generates console, html and xml reports
>* ***mutation:*** Executes mutation testing and generate reports
>
> Moreover, the provided configuration runs each test on INSTALLED packages (Not on the given sources even if obviously
> the installed packages depends on the given sources). The goal is to test definitive installed versions.

### Run linter

> ```sh
> ./project.py lint
> ```
or
> ```sh
> python project.py lint
> ```

> ***Note:** `json` and `txt` reports will be available in `build/reports/lint`.*

> ***Note:** By default this template uses [pylint](https://pylint.org/) as linter. You will find the linter
> configuration in the [pyproject.toml](./pyproject.toml) file (`[tool.pylint....]` sections).*

> ***Note:** This command uses [tox](#run-tox) but only in order to call the linter.*

### Run tests

This project is configured to execute tests with [**Pytest**](https://docs.pytest.org/):

> ```sh
> ./project.py test
> ```
or
> ```sh
> python project.py test
> ```

> ***Note:** `html`, `json` and `xml` reports will be available in `build/reports/coverage`.*

> ***Note:** If you change the project structure, don't forget to update the `[tool.pytest.ini_options]` section from
> the [pyproject.toml](./pyproject.toml) file.*

> ***Note:** This command uses [tox](#run-tox) but only in order to run your tests.*

### Run mutation

This template provides mutation testing by using [**mutmut**](https://mutmut.readthedocs.io/en/latest/):

> ```sh
> ./project.py mut
> ```
or
> ```sh
> python project.py mut
> ```

> ***Note:** `html` report will be available in `build/reports/mutation`.*

> ***Note:** If you change the project structure, don't forget to update the [pyproject.toml](./pyproject.toml) file.*

> ***Note:** This command uses [tox](#run-tox) but only in order to run your tests.*

### Build

#### Wheel archive

> ```sh
> ./project.py wheel
> ```
or
> ```sh
> python project.py wheel
> ```

#### Source Distribution archive

If you need a source distribution (sdist) archive:

> ```sh
> ./project.py sdist
> ```
or
> ```sh
> python project.py sdist
> ```

### Delivery *(on https://pypi.org/)*

> ```sh
> ./project.py upload
> ```
or
> ```sh
> python project.py upload
> ```

> ***Note:** Obviously, this command must be executed after the [Build](#build) one.*

## Docker

**<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/25px-Warning.svg.png" alt="warning-icon" width="20px" height="20px"/>
WARNING This part requires [docker](https://www.docker.com/) to be installed**

### Dev environment

If you haven't a python/poetry environment installed, PYMSDL template provides you a "ready to work" Dockerfile:

#### Build the pymsdl:devenv docker image

> ```sh
> docker build -t pymsdl:devenv-1.0.0 -f docker/devenv/Dockerfile .
> ```

#### Run the pymsdl:devenv environment

> ```sh
> docker run --rm -it --name pymsdl-dev-env -v ${PWD}:/app pymsdl:devenv-1.0.0
> ```

It opens a `sh` on a well configured python/poetry environment.

> ***Note:** you have to use the volume (`-v`) option in order to mount your project files into the container `/app`
> directory. This is useful for staying up to date with your updates.*

Now, you are ready to work (see [Quickstart](#quickstart)).

### Docker application image delivery

> ***Note:** this step is **useless** if you are working on a python package/Library/Framework to share (ie, not
> an application) because in these cases you want to publish your sdist or/and wheel archive(s).*

#### Build your docker image

PYMSDL template provides a Dockerfile in order to build an image for your application based on a generated `wheel`
distribution (See: [Dockerfile](docker/app/Dockerfile))).

> ***Note:** this Dockerfile is a "generic" one in order to provide a starting docker image distribution solution. You
> can (/should) update (/rewrite) it in order to adapt it to your application (see:
> [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)).*

> **Build image command:**
> ```sh
> docker build \
>   -f docker/app/Dockerfile \
>   -t <DOCKER_IMG_NAME>:<VERSION> \
>   --build-arg wheel_name=<WHEEL_NAME> \
>   --build-arg entrypoint=<ENTRYPOINT_VALUE> \
>   --build-arg cmd=<CMD_VALUE> \
>   .
> ```

Where:

* `<DOCKER_IMG_NAME>`: Is your docker image name
* `<VERSION>`: Is your docker image version
* `<WHEEL_NAME>`: ***[REQUIRED]*** Is the `wheel` archive name to install from the `dist` directory
* `<ENTRYPOINT_VALUE>`: *[OPTIONAL: default is `python`]* Is the docker file ENTRYPOINT
* `<CMD_VALUE>`: *[OPTIONAL: default cmd is empty]* Is the dockerfile CMD

> ***Note:** Obviously, this command must be executed after the [Wheel archive](#wheel-archive) one.*

> ***Note:** Using an `entrypoint` with an empty `cmd` provides the possibility for the end user to use `cmd` as your
> project parameters (argv). Moreover, you can use `cmd` in order to define your default project parameters.*

> **Example with the provided `hellopymsdl` sample application:**
>
> First we create a wheel archive with `./project.py wheel`.
>
> ***Note:** your `dist` directory can contain several versions (/`wheel` archives)*
>
> **- Build docker image from *python entry point* example:**
>
> The `hellopymsdl` project provides an `hello` entry point (See: [pyproject.toml](./pyproject.toml)).
> ```sh
> docker build \
>   -f docker/app/Dockerfile \
>   -t  hellopymsdl:1.0.1 \
>   --build-arg wheel_name=hellopymsdl-1.0.1-py3-none-any.whl \
>   --build-arg entrypoint=hello \
>   .
> ```
>
> **- Build docker image from *module* example:**
> ```sh
> docker build \
>   -f docker/app/Dockerfile \
>   -t  hellopymsdl:1.0.1 \
>   --build-arg wheel_name=hellopymsdl-1.0.1-py3-none-any.whl \
>   --build-arg entrypoint="python -m hellopymsdl.__main__" \
>   .
> ```
> Run the `__main__.py` module from `hellopymsdl` package.
>
> **- Build docker image from *package* example:**
>
> The `hellopymsdl` project provided an `hello` entry point (See: [pyproject.toml](./pyproject.toml)).
> ```sh
> docker build \
>   -f docker/app/Dockerfile \
>   -t  hellopymsdl:1.0.1 \
>   --build-arg wheel_name=hellopymsdl-1.0.1-py3-none-any.whl \
>   --build-arg entrypoint="python -m hellopymsdl" \
>   .
> ```
> ***Note:** your package MUST contains a `__main__.py` module.*
>
> **- Build docker image without `entrypoint` build-arg:**
>
> if you don't define the `entrypoint` build-arg, the default one is `python`. So if you run your image
> without any argument (or `cmd` build-arg) it will open a python console in an environment where your project is
> installed

> ***Trick:** If you want to build the last updated wheel (not the last version but the last built archive) you can use
> `--build-arg wheel_name=$(ls -1At dist/ | head -1)`*

#### Run your docker image

Once your docker image is ready, you can run it

> ```sh
> docker run --rm  <DOCKER_IMG_NAME>:<VERSION>
> ```

Where:

* `<DOCKER_IMG_NAME>`: Is your docker image name
* `<VERSION>`: Is your docker image version

> **Example with the provided `hellopymsdl` sample application:**
> ```
> docker run --rm --name hellopymsdl hellopymsdl:1.0.1
> ```
>
> ***Note:** Since we used only the `entrypoint` build-arg in our previous samples, if you have to pass arguments (argv)
> to your project you can do it directly like this:*
> ```
> docker run --rm --name hellopymsdl hellopymsdl:1.0.1 arg-1 arg-2 ... arg-N
> ```
>
> *Moreover, you can define default values for your project parameters. To do that, you have to use the `cmd` build-arg
> like this:*
> ```sh
> docker build \
>   -f docker/app/Dockerfile \
>   -t  hellopymsdl:1.0.1 \
>   --build-arg wheel_name=hellopymsdl-1.0.1-py3-none-any.whl \
>   --build-arg entrypoint=hello \
>   --build-arg cmd="arg-1 arg-2 ... arg-N" \
>   .
> ```
> ***Note:** You can override the default `cmd` by using the previous command line sample.*

#### Push your docker image

In order to push your image into a repository (like [Docker Hub](https://hub.docker.com/)), you will have to use the
`docker push` command line.

See [Docker repositories](https://docs.docker.com/docker-hub/repos/)

## Workflows

The PYMSDL template provides a simple [GitHub Actions](https://github.com/features/actions) workflow in order to check
and manage your project (See: [.github](.github)).

### CI

This workflow is executed on *pull_request* or *push on main*. It aims to check your project quality. To do that the
following steps are executed:

* Build archives
* Lint
* Unit tests
* Mutation tests
* Check dependencies vulnerabilities

See: [ci.yml](.github/workflows/ci.yml)

> ***Note:** if you want to reuse the
> ![ci](https://github.com/dev4py/pymsdl_template/actions/workflows/ci.yml/badge.svg?event=push&branch=main) badge for
> your project, don't forget to update the link.*

### On_release

This workflow is used in order to publish your project into [pypi](https://pypi.org/).

By default, PYMSDL template try to publish your project into [pypi](https://pypi.org/) when you publish a new release.

> ***Note:** A `PYPI_API_TOKEN` secret must be configured as pipy API key
> (See: [pypi api token](https://pypi.org/help/#apitoken)).*

> **<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/25px-Warning.svg.png" alt="warning-icon" width="20px" height="20px"/>
> WARNING:** [pypi](https://pypi.org/) doesn't allow to override an existing package version. You have to update your
> project version in the [pyproject.toml](./pyproject.toml) file to a not existing one before publish a new release.
> Otherwise, the workflow will fail.

> ***Note:** This workflow doesn't execute tests again because released version should be on `main` branch and this
> branch is configured to be protected (only pull requests can be merged on it which implies the [CI workflow](#ci) is
> executed first).*

See: [on_release.yml](.github/workflows/on_release.yml).

> ***Note:** if you want to reuse the
> ![Last release](https://github.com/dev4py/pymsdl_template/actions/workflows/on_release.yml/badge.svg) badge for your
> project, don't forget to update the link.*

You can find the `hellopymsdl` sample project published [here](https://pypi.org/project/hellopymsdl/)

> ***Note:** it means you can run `pip install hellopymsdl`.*

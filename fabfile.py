#!/usr/bin/env python
import os
from fabric.api import task, local
from fabs.common import timed, virtual
from fabs.common import logger as log
from fabs import LVENV, CVENV
from fabs import coi, tempest, snap, devstack, redhat


@timed
def venv(private=False):
    log.info("Installing packages from requirements")
    # local("sudo apt-get install -y $(cat requirements_packages)")
    venv_path = CVENV
    if private:
        venv_path = LVENV
    if not os.path.exists(venv_path):
        log.info("Creating virtual environment in {dir}".format(dir=venv_path))
        local("virtualenv --setuptools %s" % venv_path)
    else:
        log.info("Virtual environment in {dir} already exists".format(dir=venv_path))


@timed
@virtual
def requirements():
    log.info("Installing python modules from requirements")
    local("pip install -Ur requirements")


@task
@virtual
def flake8():
    ''' Make a PEP8 check for code '''
    local("flake8 --max-line-length=120 --show-source --exclude=.env1 . || echo")


@task
@virtual
def test():
    ''' For testing purposes only '''
    log.info("Testing something")
    a = local("which python")
    print a.real_command


@task(default=True)
@timed
def init(private=False):
    ''' Prepare virtualenv and install all requirements '''
    venv(private=private)
    requirements()
# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
"""
Utility functions for the brood_diff library.
"""

import contextlib
import os
import shutil
import stat
import tempfile
from collections import defaultdict
from itertools import product

from typing import Tuple

import click

from brood_diff.diff import get_index
from brood_diff import valid


@click.group()
def cli():
    """ Utility functions for interacting with Brood indices."""
    pass


# cli wrappers #
@cli.command("get-size")
@click.option('--repository', '-r', multiple=True, type=str,
              callback=valid.validate_org_repos,
              help=("<org/repo> Must be in EDS/Hatcher format: `org/repo`"
                    "\ne.g. enthought/free"))
@click.option('--platform', '-p', multiple=True, type=str,
              callback=valid.validate_platforms,
              help="<platform> See list-platforms for supported platforms")
@click.option('--version', '-v', multiple=True, type=str,
              callback=valid.validate_versions,
              help=("<python-version> See list-versions for "
                    "supported python version tags"))
def cli_get_repo_size(repository, platform, version):
    """ Query Brood indices and calculate repo size using the egg metadata.
    Reports total size of repo per platform in Gb.
    """
    sizes = get_repo_size_by_platform(repository, platform, version)
    click.secho("Repos: {}".format(repository), fg='green')
    for key in sizes.keys():
        click.secho("{} has size {} Gb".format(key, sizes[key]), fg='green')


@contextlib.contextmanager
def temporary_directory():
    """ Generate a temporary directory."""
    tempdir = tempfile.mkdtemp()
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir, onerror=_remove_readonly)


def _remove_readonly(func, path, _):
    """ Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def get_repo_size_by_platform(repos: Tuple[str],
                              plats: Tuple[str],
                              vers: Tuple[str]) -> dict:
    """ Sum the size egg metadata for a given repo by platform.

    INPUTS:
    repos: tuple of strings in Hatcher/Brood org/repo format
    plats: tuple of platform strings
    vers: tuple of python version strings

    RETURNS:
    dict containing repo sizes in Gb by platform
    """

    sizes = defaultdict(int)
    for repo, plat, ver in product(repos, plats, vers):
        org, repo = repo.split("/")
        idx = get_index(url="https://packages.enthought.com",
                        org=org,
                        repo=repo,
                        plat=plat,
                        pyver=ver)
        for key in idx.keys():
            sizes[plat] += idx[key]['size']

    for key in sizes.keys():
        sizes[key] /= 1_000_000_000
    return sizes


if __name__ == '__main__':
    cli()

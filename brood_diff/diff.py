# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
"""
Brood-diff is a CLI for calculating the diff between two given brood indices.

This is useful when determining what is required to sync a customer's
air-gapped brood instance with the Enthought brood, and is a replacement to
the old method of requiring an entire hatcher export of the Enthought brood.

Usage:
    Get Index:
    Use this function to generate the json representation of a brood index

    python diff.py get-index -u <brood-url>
                                   -r <org/repo>
                                   -p <platform>
                                   -v <python-tag>
                                   -o <path-to-output-file>

    Index Diff:
    Use this function to calculate the difference between two brood indices.
    python diff.py gen-diff -l <path-to-local-index>
                            -r <path-to-remote-index>
                            -o <path-to-output-file>

"""
import json
import sys
from typing import Iterable, NoReturn, Tuple, Union

import click
import requests

from brood_diff import valid


INDEX_ROUTE = "api/v1/json/indices"
LEGACY_INDEX_ROUTE = "api/v0/json/indices"


@click.group()
def cli():
    """ Brood diff is a CLI tool for calculating the difference between
    two different EDS indices.
    """
    pass


# CLI wrappers #


@cli.command(name="get-index")
@click.option('--url', '-u', type=str,
              help="<EDS URL> Must include http or https as needed")
@click.option('--repository', '-r', type=str, callback=valid.validate_org_repo,
              help=("<org/repo> Must be in EDS/Hatcher format: `org/repo`"
                    "\ne.g. enthought/free"))
@click.option('--platform', '-p', type=str, callback=valid.validate_platform,
              help="<platform> See list-platforms for supported platforms")
@click.option('--version', '-v', type=str, callback=valid.validate_version,
              help=("<python-version> See list-versions for "
                    "supported python version tags"))
@click.option('--output', '-o', type=str,
              help="<path> Full path to output json file")
@click.option('--sort/--no-sort', default=True,
              help=("Set whether the output should be sorted."
                    "\nDefault: --sort"))
@click.option('--legacy/--no-legacy', default=False,
              help=("Use --legacy for the legacy v0 api version. Note, this "
                    "should be used only in special circumstances."
                    "\nDefault: --no-legacy"))
def cli_get_index(url, repository, platform, version, output, sort, legacy):
    """ Get index for a given repo/platform/python-tag from EDS instance
    located at url specified by -u/--url and write output to file
    specified by -o/--output."""

    org, repo = repository.split("/")

    idx = get_index(url,
                    org,
                    repo,
                    platform,
                    version,
                    legacy)
    click.echo("Writing output to json sort={} ...".format(sort))
    to_json_file(idx, output, sort=sort)


@cli.command(name='full-index')
@click.option('--url', '-u', type=str,
              help="<EDS URL> Must include http or https as needed")
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
@click.option('--output', '-o', type=str,
              help="<path> Full path to output json file")
@click.option('--sort/--no-sort', default=True,
              help=("Set whether the output should be sorted."
                    "\nDefault: --sort"))
@click.option('--legacy/--no-legacy', default=False,
              help=("Use --legacy for the legacy v0 api version. Note, this "
                    "should be used only in special circumstances."
                    "\nDefault: --no-legacy"))
def cli_get_full_index(url, repository, platform, version, output, sort,
                       legacy):
    """ Get full json representation of multiple EDS indices from an EDS
    instance specified by -u/--url for potentially multiple platforms,
    repositories, and python versions, and output the full index as a single
    json file specified by -o/--output."""

    gen_full_index(url,
                   repository,
                   platform,
                   version,
                   output,
                   sort,
                   legacy)


@cli.command(name="gen-diff")
@click.option('--local', '-l', type=str,
              help="<path> Full path to json file for local index")
@click.option('--remote', '-r', type=str,
              help="<path> Full path to json file for remote index")
@click.option('--output', '-o', type=str,
              help="<path> Full path to output json file")
def cli_gen_diff(local, remote, output):
    """ Calculate the difference between two EDS indices and output the
    result as a json file.

    Note, the terminology used is from the perspective of the EDS end-user.

    Thus the local index represents the index you wish to compare to the
    remote (Enthought) index.

    Example Use Case:

    End-user runs get-index on their local EDS to generate the index of
    their enthought/free repo as a json file: local.json.

    Next, run the same command against the Brood production server to generate
    the index of our enthought/free repo as a json file: remote.json.

    Finally run python diff.py gen-diff -l local.json -r remote.json -o
    output_file.json
    """
    local_index = from_json_file(local)
    remote_index = from_json_file(remote)
    diff = index_diff(local_index, remote_index)
    to_json_file(diff, output)


@cli.command(name="full-diff")
@click.option('--local', '-l', type=str,
              help="<path> Full path to json file for local index")
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
@click.option('--output', '-o', type=str,
              help="<path> Full path to output json file")
@click.option('--sort/--no-sort', default=True,
              help=("Set whether the output should be sorted."
                    "\nDefault: --sort"))
@click.option('--legacy/--no-legacy', default=False,
              help=("Use --legacy for the legacy v0 api version. Note, this "
                    "should be used only in special circumstances."
                    "\nDefault: --no-legacy"))
def cli_full_diff(local, repository, platform,
                  version, output, sort, legacy=False):
    """ Given a local index son file, calculate the difference between that
    index and the Enthought production EDS repos specified by the repo,
    platform, and version options.

    The output is a single json file containing the missing packages.
    """
    full_diff(local,
              repository,
              platform,
              version,
              output,
              sort,
              legacy)


@cli.command(name="list-platforms")
def list_platforms():
    """ List valid input for platform option."""
    click.echo("Valid Platforms:")
    for plat in sorted(valid.PLATS):
        click.echo(plat)


@cli.command(name="list-versions")
def list_versions():
    """ List valid input for version option."""
    click.echo("Valid Python Version tags:")
    for ver in sorted(valid.VERS):
        click.echo(ver)


# tested functions #


def get_index(url: str, org: str, repo: str, plat: str, pyver: str,
              legacy: bool = False) -> Union[dict, NoReturn]:
    """ Fetch index for a given repo/platform/python-tag."""
    if legacy:
        resource = "/".join((url, LEGACY_INDEX_ROUTE,
                             org, repo, plat, pyver, "eggs"))
    else:
        resource = "/".join((url, INDEX_ROUTE, org, repo, plat, pyver, "eggs"))
    print("Requesting {} ...".format(resource))
    r = requests.get(resource)
    if r.status_code == 200:
        return r.json()
    elif r.status_code in (400, 404):
        # incorrect base url raises ConnectionError and plat and ver get
        # validated via CLI - thus 404 likely indicates problem with org/repo.
        print("HTTP 404 Error: Please double check your Repository settings.")
        print("Repository must be a valid org/repo combination.")
        r.raise_for_status()
        sys.exit()
    elif r.status_code in (500, 502, 503, 504):  # Brood internal errors
        msg = "HTTP 50* Error: Please verify that the EDS instance is up at {}"
        print(msg.format(url))
        r.raise_for_status()
        sys.exit()


def gen_full_index(url: str, org_repos: Tuple[str], plats: Tuple[str],
                   pyvers: Tuple[str], output: str, sort: bool = True,
                   legacy: bool = False) -> None:
    """ Given a set of org/repo, platforms, and versions, generate a single
    json file containing the entirety of the index representing these repos.

    The most common usecase would be to collect the full index of the
    end-user's enthought/free + enthought/gpl and potentially also
    enthought/lgpl repos.
    """
    full_index = {}
    for org_repo in org_repos:
        org, repo = org_repo.split("/")
        for plat in plats:
            for ver in pyvers:
                full_index.update(get_index(url,
                                            org,
                                            repo,
                                            plat,
                                            ver,
                                            legacy))
    to_json_file(full_index, output, sort=sort)


def index_diff(local_index: dict, remote_index: dict) -> dict:
    """ Calculate the difference between two json brood indices.
    Adapted from brood/brood/sync/egg_sync.py

    Remove calculations for eggs to delete:
    Unless user specifically requests that we remove unused or outdated eggs
    we should make minimal changes to their local EDS instance.

    Likewise, remove calculations for eggs to move
    """
    local_index_set = set(local_index)
    remote_index_set = set(remote_index)

    missing_egg_names = remote_index_set - local_index_set
    missing_egg_index = {key: remote_index[key]
                         for key in missing_egg_names}

    return {"missing": missing_egg_index}


def full_diff(local_idx_json: str, org_repos: Tuple[str],
              plats: Tuple[str], vers: Tuple[str],
              output: str,
              sort: bool = True,
              legacy: bool = False,
              remote_url: str = "https://packages.enthought.com"):
    """ Given set of org/repo/plat/ver, a local index file and remote EDS host,
    calculate the full index diff and write to json file specified by the
    parameter, output.

    remote_url is left as an internally available parameter but not exposed
    via the cli - in general we will target the enthought production url.
    """
    local_idx = from_json_file(local_idx_json)
    remote_idx = {}
    for org_repo in org_repos:
        for plat in plats:
            for ver in vers:
                org, repo = org_repo.split("/")
                remote_idx.update(get_index(remote_url,
                                            org,
                                            repo,
                                            plat,
                                            ver,
                                            legacy))
    diff = index_diff(local_idx, remote_idx)
    to_json_file(diff, output, sort=sort)


def to_json_file(idx: dict, path: str, sort: bool = False) -> None:
    """ Write index to file as json."""
    with open(path, 'w') as f:
        json.dump(idx, f, sort_keys=sort)


def from_json_file(path: str) -> dict:
    """ Read index from json file."""
    with open(path, 'r') as f:
        return json.loads(f.read())


def merge_json(input_paths: Iterable[str], output) -> None:
    """ Given list of paths to json indices, merge into one json file."""
    index = {}
    for path in input_paths:
        index.update(from_json_file(path))
    to_json_file(index, output, sort=True)


if __name__ == '__main__':
    cli()

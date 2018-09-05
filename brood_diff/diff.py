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


BASE_URL = "https://packages2.enthought.com"
INDEX_ROUTE = "api/v1/json/indices"
LEGACY_INDEX_ROUTE = "api/v0/json/indices"


@click.group()
def cli():
    """ Container group for all cli commands."""
    pass


# CLI wrappers #


@cli.command(name="get-index")
@click.option('--url', '-u', type=str)
@click.option('--repository', '-r', type=str,
              help="Repository must be in format `org/repo`")
@click.option('--platform', '-p', type=str)
@click.option('--version', '-v', type=str)
@click.option('--output', '-o', type=str)
@click.option('--sort/--no-sort', default=True)
@click.option('--legacy/--no-legacy', default=False,
              help="USe --legacy for the legacy v0 API")
def cli_get_index(url, repository, platform, version, output, sort, legacy):
    """ CLI wrapper for get_index + to_json pipeline."""
    if valid.validate_org_repo(repository):
        org, repo = repository.split("/")
    else:
        click.echo("Repository must be in format `org/repo`")
        return
    if not valid.validate_platform(platform):
        click.secho("Invalid platform specification: {}".format(platform),
                    fg='red')
        click.echo("For a list of valid platforms: diff.py list-platforms.")
        return
    if not valid.validate_version(version):
        click.secho("Invalid version specification: {}".format(version),
                    fg='red')
        click.echo("For a list of valid versions: diff.py list-versions.")
        return

    idx = get_index(url,
                    org,
                    repo,
                    platform,
                    version,
                    legacy)
    click.echo("Writing output to json sort={} ...".format(sort))
    to_json_file(idx, output, sort=sort)


@cli.command(name='full-index')
@click.option('--local', '-l', type=str)
@click.option('--repository', '-r', multiple=True, type=str,
              help="Repository must be in format `org/repo`")
@click.option('--platform', '-p', multiple=True, type=str)
@click.option('--version', '-v', multiple=True, type=str)
@click.option('--output', '-o', type=str)
def cli_get_full_index(local, repository, platform, version, output):
    """ CLI wrapper for gen_full_index."""
    gen_full_index(local,
                   repository,
                   platform,
                   version,
                   output)


@cli.command(name="gen-diff")
@click.option('--local', '-l', type=str)
@click.option('--remote', '-r', type=str)
@click.option('--output', '-o', type=str)
def cli_gen_diff(local, remote, output):
    """CLI wrapper for index_diff.

    Note, the terminology used is from the perspective of the EDS customer.
    Thus the local index represents the index you wish to test against the
    remote (Enthought) index.

    Example:
    Have customer run get-index on their local EDS to generate the index of
    their enthought/free repo as a json file - local.json.
    Next, run the same command against the Brood production server to generate
    the index of our enthought/free repo as a json file - remote.json.
    Finally run gen-diff -l local.json -r remote.json
    """
    local_index = from_json_file(local)
    remote_index = from_json_file(remote)
    diff = index_diff(local_index, remote_index)
    to_json_file(diff, output)


@cli.command(name="full-diff")
@click.option('--local', '-l', type=str)
@click.option('--repository', '-r', multiple=True, type=str,
              help="Repository must be in format `org/repo`")
@click.option('--platform', '-p', multiple=True, type=str)
@click.option('--version', '-v', multiple=True, type=str)
@click.option('--output', '-o', type=str)
@click.option('--legacy/--no-legacy', default=False,
              help="Use --legacy for the legacy v0 API")
def cli_full_diff(local, repository, platform,
                  version, output, legacy=False):
    """ CLI Wrapper for the full diff calculation pipeline.
    Assuming a local index json file has been generated by the client, this
    function can be called to calculate the difference between the client's
    repos and the Enthought production repos.

    The output is a single json file containing the missing packages
    """
    full_diff_pipeline(local,
                       repository,
                       platform,
                       version,
                       output,
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
                   pyvers: Tuple[str], output: str,
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
    to_json_file(full_index, output, sort=True)


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


def full_diff_pipeline(local_idx_json: str, org_repos: Tuple[str],
                       plats: Tuple[str], vers: Tuple[str],
                       output: str,
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
    to_json_file(diff, output, sort=True)


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

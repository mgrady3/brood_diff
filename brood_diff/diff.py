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

import click
import json
import requests
import sys

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
              help="set to True to use legacy v0 api")
def cli_get_index(url, repository, platform, version, output, sort, legacy):
    """ CLI wrapper for get_index + to_json pipeline."""
    try:
        org, repo = repository.split("/")
    except ValueError:
        click.echo("Repository must be in format `org/repo`")
        return
    if platform not in valid.PLATS:
        click.echo("Invalid platform specification: {}".format(platform),
                   fg='red')
        click.echo("For a list of valid platforms: diff.py list-platforms.")
        return
    if version not in valid.VERS:
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


@cli.command(name="gen-diff")
@click.option('--local', '-l', type=str)
@click.option('--remote', '-r', type=str)
@click.option('--output', '-o', type=str)
def cli_gen_diff(local, remote, output):
    """CLI wrapper for index_diff."""
    local_index = from_json_file(local)
    remote_index = from_json_file(remote)
    diff = index_diff(local_index, remote_index)
    to_json_file(diff, output)


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


def get_index(url: str, org: str, repo: str,
              plat: str, pyver: str, legacy: bool = False) -> dict:
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
    elif r.status_code == 404:
        # incorrect base url raises ConnectionError and plat and ver get
        # validated via CLI - thus 404 likely indicates problem with org/repo.
        print("HTTP 404 Error: Please double check your Repository settings.")
        print("Repository must be a valid org/repo combination.")
        r.raise_for_status()
        sys.exit()


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


def to_json_file(idx: dict, path: str, sort: bool = False) -> None:
    """ Write index to file as json."""
    with open(path, 'w') as f:
        json.dump(idx, f, sort_keys=sort)


def from_json_file(path: str) -> dict:
    """ Read index from json file."""
    with open(path, 'r') as f:
        return json.loads(f.read())


if __name__ == '__main__':
    cli()

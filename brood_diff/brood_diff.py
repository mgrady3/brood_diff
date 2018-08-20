"""
Brood-diff is a CLI for calculating the diff between two given brood indices.

This is useful when determining what is required to sync a customer's
air-gapped brood instance with the Enthought brood, and is a replacement to
the old method of requiring an entire hatcher export of the Enthought brood.

Usage:

"""

import click
import json
import requests

# from typing import Optional

BASE_URL = "https://packages2.enthought.com"
INDEX_ROUTE = "api/v1/json/indices"


@click.group()
def cli():
    """ Container group for all cli commands."""
    pass


# CLI wrappers
@cli.command(name="get-index")
@click.option('--url', '-u', type=str)
@click.option('--repository', '-r', type=str,
              help="Repository must be in format `org/repo`")
@click.option('--platform', '-p', type=str)
@click.option('--version', '-v', type=str)
@click.option('--output', '-o', type=str)
def cli_get_index(url, repository, platform, version, output):
    try:
        org, repo = repository.split("/")
    except ValueError:
        click.echo("Repository must be in format `org/repo`")
        return
    idx = get_index(url,
                    org,
                    repo,
                    platform,
                    version)
    to_json_file(idx, output)


# tested functions


def get_index(url: str, org: str, repo: str,
              plat: str, pyver: str) -> dict:
    """ Fetch index for a given repo/platform/python-tag."""
    resource = "/".join((url, INDEX_ROUTE, org, repo, plat, pyver, "eggs"))
    print("Requesting {} ...".format(resource))
    r = requests.get(resource)
    return r.json()


def index_diff(local_index: dict, remote_index: dict) -> dict:
    """
    """
    local_index_set = set(local_index)
    remote_index_set = set(remote_index)

    missing_egg_names = remote_index_set - local_index_set
    missing_egg_index = {key: remote_index[key]
                         for key in missing_egg_names}

    delete_egg_names = local_index_set - remote_index_set
    delete_egg_index = {key: local_index[key]
                        for key in delete_egg_names}

    return {"missing": missing_egg_index, "delete": delete_egg_index}


def to_json_file(idx: dict, path: str) -> None:
    """ Write index to file as json."""
    with open(path, 'w') as f:
        json.dump(idx, f)


def from_json_file(path: str) -> dict:
    """ Read index from json file."""
    with open(path, 'r') as f:
        return json.loads(f.read())


if __name__ == '__main__':
    cli()

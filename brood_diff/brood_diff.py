"""
Brood-diff is a CLI for calculating the diff between two given brood indices.

This is useful when determining what is required to sync a customer's 
air-gapped brood instance with the Enthought brood, and is a replacement to
the old method of requiring an entire hatcher export of the Enthought brood.

Usage:

"""

import click
import requests

BASE_URL = "https://packages2.enthought.com/api/v1/json/indices"

@click.group()
def cli():
    """ Container group for all cli commands."""
    pass

def get_index(org: str, repo: str, plat: str, pyver: str) -> dict:
    resource = "/".join((BASE_URL, org, repo, plat, pyver, "eggs"))
    try:
        r = requests.get(resource)
    # TODO: Handle HTTP errors appropriately
    except exception as e:
        print(e)
    return r.json()
# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#

import click


PLATS = ["osx-x86",
         "rh5-x86",
         "win-x86",
         "osx-x86_64",
         "rh5-x86_64",
         "win-x86_64",
         "rh6-x86",
         "rh6-x86_64",
         "rh7-x86",
         "rh7-x86_64"]

VERS = ["cp27",
        "cp34",
        "cp35",
        "cp36",
        "pp27"]


def validate_platform(ctx: click.Context, plat: str):
    """ Validate User CLI input."""
    if plat in PLATS:
        return plat
    else:
        raise click.BadParameter(
            ("Invalid platform {}. Please use list-platforms for a list of"
             " supported platforms.".format(plat)))


def validate_version(ctx: click.Context, ver: str):
    """ Validate User CLI input."""
    if ver in VERS:
        return ver
    else:
        raise click.BadParameter(
            ("Invalid python version {}. Please use list-platforms for a list"
             " of supported platforms.".format(ver)))


def validate_org_repo(ctx: click.Context, org_repo: str):
    """ Validate User CLI input."""
    if "/" in org_repo and len(org_repo.split("/")) == 2:
        return org_repo
    else:
        raise click.BadParameter(
            ("Invalid repository format {}. Repositories must use the"
             " EDS/Hatcher format <org/repo>."
             "e.g. enthought/free".format(org_repo)))

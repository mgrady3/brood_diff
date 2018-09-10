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


def validate_platform(ctx: click.Context,
                      param: click.core.Option,
                      value: str):
    """ Validate User CLI input."""
    if value in PLATS:
        return value
    else:
        raise click.BadParameter(
            ("Invalid platform: {}. Please use list-platforms for a list of"
             " supported platforms.".format(value)))


def validate_version(ctx: click.Context,
                     param: click.core.Option,
                     value: str):
    """ Validate User CLI input."""
    if value in VERS:
        return value
    else:
        raise click.BadParameter(
            ("Invalid python version: {}. Please use list-platforms for a list"
             " of supported platforms.".format(value)))


def validate_org_repo(ctx: click.Context,
                      param: click.core.Option,
                      value: str):
    """ Validate User CLI input.
    Repositories are formatted using the EDS/Hatcher format <org/repo> - e.g.
        enthought/free
    """
    if "/" in value and len(value.split("/")) == 2:
        return value
    else:
        raise click.BadParameter(
            ("Invalid repository format: {}. Repositories must use the"
             " EDS/Hatcher format <org/repo>."
             "e.g. enthought/free".format(value)))

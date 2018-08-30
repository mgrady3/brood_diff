# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#


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


def validate_platform(plat: str):
    """ Validate User CLI input."""
    return plat in PLATS


def validate_version(ver: str):
    """ Validate User CLI input."""
    return ver in VERS


def validate_org_repo(org_repo: str):
    """ Validate User CLI input."""
    return "/" in org_repo and len(org_repo.split("/")) == 2

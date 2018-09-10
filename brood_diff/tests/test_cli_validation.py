# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
import click
import pytest

from brood_diff import valid


class TestValidation(object):
    """ Testing of CLI option validation."""

    def test_validate_platform(self):
        # given
        good_plat = "osx-x86_64"
        bad_plat = "osx-x87_64"
        ctx = None
        param = None

        # when
        g_plat = valid.validate_platform(ctx, param, good_plat)

        with pytest.raises(click.BadParameter) as execinfo:
            valid.validate_platform(ctx, param, bad_plat)

        # then
        assert g_plat == good_plat
        assert "Invalid platform" in str(execinfo.value)

    def test_validate_version(self):
        # given
        good_vers = "cp36"
        bad_vers = "cp16"
        ctx = None
        param = None

        # when
        g_vers = valid.validate_version(ctx, param, good_vers)

        with pytest.raises(click.BadParameter) as execinfo:
            valid.validate_version(ctx, param, bad_vers)

        # then
        assert g_vers == good_vers
        assert "Invalid python version" in str(execinfo.value)

    def test_validate_repository(self):
        # given
        good_repo = "enthought/free"
        bad_repo = "enthought free"
        ctx = None
        param = None

        # when
        g_repo = valid.validate_org_repo(ctx, param, good_repo)

        with pytest.raises(click.BadParameter) as execinfo:
            valid.validate_org_repo(ctx, param, bad_repo)

        # then
        assert g_repo == good_repo
        assert "Invalid repository" in str(execinfo.value)

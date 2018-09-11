# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
import click
import pytest

from brood_diff import valid


class TestValidation(object):
    """ Testing of CLI option validation."""

    def test_validate_platforms(self):
        good_plats = ("osx-x86_64", "rh6-x86_64", "win-x86_64")
        bad_plats = ("osx-x87_64", "rh6-x86_64", "win-x86_64")
        ctx = None
        param = None

        # when
        g_plats = valid.validate_platforms(ctx, param, good_plats)

        with pytest.raises(click.BadParameter) as execinfo:
            valid.validate_platforms(ctx, param, bad_plats)

        # then
        assert g_plats == good_plats
        assert "Invalid platform(s)" in str(execinfo.value)
        assert "osx-x87_64" in str(execinfo.value)

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

    def test_validate_versions(self):
        # given
        good_vers = ("cp36", "cp35", "cp27")
        bad_vers = ("cp16", "cp35", "cp27")
        ctx = None
        param = None

        # when
        g_vers = valid.validate_versions(ctx, param, good_vers)

        with pytest.raises(click.BadParameter) as execinfo:
            valid.validate_versions(ctx, param, bad_vers)

        # then
        assert g_vers == good_vers
        assert "Invalid python version(s)" in str(execinfo.value)
        assert "cp16" in str(execinfo.value)

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

    def test_validate_repositories(self):
        # given
        good_repos = ("enthought/free", "enthought/gpl", "an_org/a_repo")
        bad_repos = ("enthought free",  "enthought/gpl", "an_org/a_repo")
        ctx = None
        param = None

        # when
        g_repos = valid.validate_org_repos(ctx, param, good_repos)

        with pytest.raises(click.BadParameter) as execinfo:
            valid.validate_org_repos(ctx, param, bad_repos)

        # then
        assert g_repos == good_repos
        assert "Invalid repository" in str(execinfo.value)
        assert "enthought free" in str(execinfo.value)

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

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

        # when
        g_plat = valid.validate_platform(ctx, good_plat)

        with pytest.raises(click.BadParameter) as execinfo:
            valid.validate_platform(ctx, bad_plat)
        
        # then
        assert g_plat == good_plat
        assert "Invalid platform" in str(execinfo.value)
        
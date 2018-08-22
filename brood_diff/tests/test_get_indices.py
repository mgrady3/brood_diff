# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
from brood_diff.brood_diff import get_index
import pytest
import requests


class TestGetIndex(object):
    """ Test getting json/dict index of a Brood instance."""

    def test_get_index_bad_url(self):
        # given
        BASE_URL = "https://packages.entought.com"  # typo
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x86_84"
        VER = "cp27"

        # when
        with pytest.raises(requests.exceptions.ConnectionError) as execinfo:
            get_index(url=BASE_URL,
                      org=ORG,
                      repo=REPO,
                      plat=PLAT,
                      pyver=VER)
        # then
        assert "Failed to establish a new connection" in str(execinfo.value)

    def test_get_index(self):
        # given
        BASE_URL = "https://packages.enthought.com"
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x86_84"
        VER = "cp27"

        # when
        idx = get_index(url=BASE_URL,
                        org=ORG,
                        repo=REPO,
                        plat=PLAT,
                        pyver=VER)
        # then
        assert isinstance(idx, dict)
        assert idx

    def test_legacy_get_index(self):
        # given
        BASE_URL = "https://packages.enthought.com"
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x86_84"
        VER = "cp27"

        # when
        idx = get_index(url=BASE_URL,
                        org=ORG,
                        repo=REPO,
                        plat=PLAT,
                        pyver=VER,
                        legacy=True)
        # then
        assert isinstance(idx, dict)
        assert idx

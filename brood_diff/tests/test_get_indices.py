# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
from brood_diff.diff import get_index
import pytest
import requests


class TestGetIndex(object):
    """ Test getting json/dict index of a Brood instance."""
    # TODO: Use test fixtures

    def test_get_index_bad_url(self):
        # given
        BASE_URL = "https://packages.entought.com"  # intentional typo
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x86_64"
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
        PLAT = "rh6-x86_64"
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

    def test_get_index_bad_org_repo(self):
        # given
        BASE_URL = "https://packages.enthought.com"
        REPO = "gpl"
        ORG = "entought"  # intentional typo
        PLAT = "rh6-x86_64"
        VER = "cp27"

        # when
        with pytest.raises(requests.HTTPError) as execinfo:
            get_index(url=BASE_URL,
                      org=ORG,
                      repo=REPO,
                      plat=PLAT,
                      pyver=VER)
        # then
        assert "Client Error" in str(execinfo.value)  # should be 404

    def test_get_index_bad_plat(self):
        """ Note: CLI validates plat + ver so this shouldn't happen when
        using the CLI but could happen if calling get_index directly.
        """
        # given
        BASE_URL = "https://packages.enthought.com"
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x87_64"  # intentional typo
        VER = "cp27"

        # when
        with pytest.raises(requests.HTTPError) as execinfo:
            get_index(url=BASE_URL,
                      org=ORG,
                      repo=REPO,
                      plat=PLAT,
                      pyver=VER)
        # then
        assert "Client Error" in str(execinfo.value)  # should be 404

    def test_get_index_bad_ver(self):
        """ Note: CLI validates plat + ver so this shouldn't happen when
        using the CLI but could happen if calling get_index directly.
        """
        # given
        BASE_URL = "https://packages.enthought.com"
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x86_64"
        VER = "cp17"  # intentional typo

        # when
        with pytest.raises(requests.HTTPError) as execinfo:
            get_index(url=BASE_URL,
                      org=ORG,
                      repo=REPO,
                      plat=PLAT,
                      pyver=VER)
        # then
        assert "Client Error" in str(execinfo.value)  # should be 400

    def test_legacy_get_index(self):
        # given
        BASE_URL = "https://packages.enthought.com"
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x86_64"
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

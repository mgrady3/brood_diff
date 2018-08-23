# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
from brood_diff.diff import get_index, to_json_file, from_json_file

import os
import pytest
import tempfile


class TestIO(object):
    # potentially useful paths for tests
    thisdir = os.path.abspath(os.path.dirname(__file__))
    srcdir = os.path.abspath(os.path.join(thisdir, os.pardir))
    rootdir = os.path.abspath(os.path.join(srcdir, os.pardir))
    test_data = os.path.join(rootdir, "test_data")

    def test_to_json_file(self):
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
        _, path = tempfile.mkstemp(suffix=".json")
        to_json_file(idx, path)

        # then
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_from_json(self):
        # given
        test_file = os.path.join(self.test_data, "idx-e-gpl-rh6-36.json")

        # when
        idx = from_json_file(test_file)

        # then
        assert isinstance(idx, dict)
        assert idx

    def test_to_from_json_round_trip(self):
        # given
        BASE_URL = "https://packages.enthought.com"
        REPO = "gpl"
        ORG = "enthought"
        PLAT = "rh6-x86_64"
        VER = "cp27"

        # when
        idx_from_brood = get_index(url=BASE_URL,
                                   org=ORG,
                                   repo=REPO,
                                   plat=PLAT,
                                   pyver=VER)

        _, path = tempfile.mkstemp(suffix=".json")
        to_json_file(idx_from_brood, path)

        idx_from_file = from_json_file(path)

        # then
        assert idx_from_brood == idx_from_file

    @pytest.mark.skip(reason="Haven't come up with reliable test yet.")
    def test_to_json_file_sorted(self):
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
        _, path = tempfile.mkstemp(suffix=".json")
        to_json_file(idx, path, sort=True)

        # then
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_read_formatted_json(self):
        """ Test reading vs-code auto json formatting."""
        # given
        test_file = os.path.join(self.test_data, "test-formatted-index.json")

        # when
        idx = from_json_file(test_file)

        # then
        assert isinstance(idx, dict)
        assert idx

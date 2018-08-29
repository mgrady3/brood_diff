# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
from brood_diff.diff import (
    get_index, to_json_file, from_json_file, merge_json, gen_full_index
)

from itertools import product
import json
import os
import pytest
import tempfile


class TestIO(object):
    # TODO: Use test fixtures
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

    def test_from_json_bad_file(self):
        # given
        # intentional typo
        test_file = os.path.join(self.test_data, "idxx-e-gpl-rh6-36.json")

        # when
        with pytest.raises(FileNotFoundError) as execinfo:
            from_json_file(test_file)

        # then
        assert "No such file or directory" in str(execinfo.value)

    def test_from_json_empty_file(self):
        # given
        test_file = os.path.join(self.test_data, "empty.json")

        # when
        with pytest.raises(json.decoder.JSONDecodeError) as execinfo:
            from_json_file(test_file)

        # then
        assert "Expecting value" in str(execinfo.value)

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

    def test_merge_json(self):
        # given
        indices = ["idx-e-free-rh6-x86_64-36.json",
                   "idx-e-gpl-rh6-x86_64-36.json",
                   "idx-e-lgpl-rh6-x86_64-36.json"]
        paths = [os.path.join(self.test_data, idx) for idx in indices]

        # when
        _, out_path = tempfile.mkstemp(suffix=".json")
        merge_json(paths, out_path)
        full_idx = from_json_file(out_path)

        # then
        for path in paths:
            idx = from_json_file(path)
            assert set(idx).issubset(set(full_idx))

    def test_gen_full_index(self):
        # given
        BASE_URL = "https://packages.enthought.com"  # intentional typo
        REPOS = ("gpl", "free")
        ORG = ("enthought",)
        PLATS = ("rh6-x86_64", "osx-x86_64")
        VERS = ("cp27", "cp35", "cp36")

        ORG_REPOS = tuple("/".join(t) for t in product(ORG, REPOS))

        _, out_path = tempfile.mkstemp(suffix=".json")

        # when
        gen_full_index(BASE_URL,
                       ORG_REPOS,
                       PLATS,
                       VERS,
                       out_path)
  
        # raises JSONDecodeError if file is empty
        idx = from_json_file(out_path)

        # then
        assert os.path.exists(out_path)
        assert os.path.isfile(out_path)
        assert idx

        # Make sure a package from each repo exists
        # enthought/free: alabaster-0.7.9-1
        # enthought/gpl: Qt-4.8.7-7
        assert "alabaster-0.7.9-1.egg" in idx.keys()
        assert "Qt-4.8.7-7.egg" in idx.keys()

# (C) Copyright 2018 Enthought, Inc., Austin, TX
# All rights reserved.
#
from brood_diff.diff import get_index, index_diff, from_json_file

import os


class TestIndexDiff(object):
    # potentially useful paths for tests
    thisdir = os.path.abspath(os.path.dirname(__file__))
    srcdir = os.path.abspath(os.path.join(thisdir, os.pardir))
    rootdir = os.path.abspath(os.path.join(srcdir, os.pardir))
    test_data = os.path.join(rootdir, "test_data")

    def test_diff_same_index(self):
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

        diff = index_diff(idx, idx)

        # then
        assert isinstance(diff, dict)
        assert not diff['missing']

    def test_diff_different_indices(self):
        # given
        BASE_URL = "https://packages.enthought.com"
        ORG = "enthought"
        REPO_GPL = "gpl"
        REPO_FREE = "free"
        PLAT = "rh6-x86_64"
        VER27 = "cp27"

        # when
        idx_gpl = get_index(url=BASE_URL,
                            org=ORG,
                            repo=REPO_GPL,
                            plat=PLAT,
                            pyver=VER27)

        idx_free = get_index(url=BASE_URL,
                             org=ORG,
                             repo=REPO_FREE,
                             plat=PLAT,
                             pyver=VER27)

        diff = index_diff(idx_gpl, idx_free)

        # then
        assert isinstance(diff, dict)
        assert diff['missing']

    def test_diff_manual_edits(self):
        """ Use test_data json files, same index, one with manual edits."""

        # when
        remote_idx = from_json_file(os.path.join(self.test_data,
                                                 "idx-e-gpl-rh6-36.json"))
        local_idx = from_json_file(os.path.join(self.test_data,
                                                "idx-e-gpl-rh6-36-edit.json"))
        diff = index_diff(local_idx, remote_idx)

        # then
        assert diff['missing']
        assert "psycopg2-2.7.3.2-1.egg" in diff['missing'].keys()

    def test_diff_both_empty(self):
        # given

        # when
        remote_idx = local_idx = {}

        diff = index_diff(local_idx, remote_idx)

        # then
        assert not diff['missing']

    def test_diff_local_empty(self):
        # given

        # when
        local_idx = {}
        remote_idx = from_json_file(os.path.join(self.test_data,
                                                 "idx-e-gpl-rh6-36.json"))

        diff = index_diff(local_idx, remote_idx)

        # then
        assert diff['missing']
        assert diff['missing'].keys() == remote_idx.keys()

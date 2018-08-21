from brood_diff.brood_diff import get_index, index_diff


class TestIndexDiff(object):

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

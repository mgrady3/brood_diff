"""
Utility functions for the brood_diff library.
"""

import contextlib
import os
import shutil
import stat
import tempfile


@contextlib.contextmanager
def temporary_directory():
    """ Generate a temporary directory."""
    tempdir = tempfile.mkdtemp()
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir, onerror=_remove_readonly)


def _remove_readonly(func, path, _):
    """ Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

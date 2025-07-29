import os
import shutil
import tempfile

import pytest


@pytest.fixture(autouse=True, scope="session")
def _tmp_reports():
    tmp = tempfile.mkdtemp()
    os.environ["REPORTS_DIR"] = tmp
    os.environ["TESTING"] = "1"
    yield
    shutil.rmtree(tmp)

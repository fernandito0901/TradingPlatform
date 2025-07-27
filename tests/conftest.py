import os
import shutil
import tempfile

import pytest


@pytest.fixture(autouse=True, scope="session")
def _tmp_reports():
    tmp = tempfile.mkdtemp()
    os.environ["REPORTS_DIR"] = tmp
    yield
    shutil.rmtree(tmp)

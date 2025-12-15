from streamlit.testing.v1 import AppTest
import pytest
from pathlib import Path



def test_appError():
    app_path = Path(__file__).resolve().parents[1] / "calculateur-app" / "app2.py"

    at = AppTest.from_file(app_path)
    at.run()


    assert at.exception is None

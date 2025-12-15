from streamlit.testing.v1 import AppTest
import pytest
from pathlib import Path



def test_appError():
    app_path = Path(__file__).resolve().parents[1] / "app2.py"

    at = AppTest.from_file(app_path)
    at.run()

    if at.exception is not None:
        print(at.exception)
        for e in at.exception:
            print("----")
            print(e)
    assert len(at.exception) == 0

import os
import pathlib


CORRIDOR_HOME = pathlib.Path(os.environ["CORRIDOR_HOME"])
os.environ["PYSPARK_PYTHON"] = str(CORRIDOR_HOME / "venv/bin/python")
os.environ["PYSPARK_SUBMIT_ARGS"] = "--master local[1] pyspark-shell"

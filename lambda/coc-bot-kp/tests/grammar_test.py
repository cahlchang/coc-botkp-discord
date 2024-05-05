import py_compile
import pytest
import glob

python_files = glob.glob("*.py", recursive=True)
python_files += glob.glob("yig/*.py", recursive=True)
python_files += glob.glob("yig/*/*.py", recursive=True)


@pytest.mark.parametrize("path", python_files)
def test_syntax(path):
    try:
        py_compile.compile(path, doraise=True)
    except py_compile.PyCompileError as ex:
        pytest.fail(ex.msg)

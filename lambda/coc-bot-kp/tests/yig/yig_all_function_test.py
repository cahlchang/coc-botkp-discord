import pytest # type: ignore
import logging
import inspect
import os
import sys
import importlib
from typing import get_type_hints

# プロジェクトのルートディレクトリをPYTHONPATHに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_py_files(directory):
    """指定されたディレクトリ内のすべての.pyファイルを再帰的に取得"""
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                py_files.append(os.path.join(root, file))
    return py_files

def import_module_from_file(file_path):
    """ファイルパスからモジュールをインポート"""
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_functions_and_classes_from_module(module):
    """モジュールからすべての関数とクラスを取得"""
    items = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            items.append(('function', name, obj))
        elif inspect.isclass(obj):
            items.append(('class', name, obj))
    return items

def check_function_arguments(func):
    """関数の引数をチェック"""
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    for param_name, param in signature.parameters.items():
        # デフォルト引数や可変長引数は除外
        if param.default is not param.empty or param.kind in [param.VAR_POSITIONAL, param.VAR_KEYWORD]:
            continue

        # 型ヒントがある場合はチェック
        if param_name in type_hints:
            assert not isinstance(type_hints[param_name], type(None)), f"Argument '{param_name}' should not have None as its type hint"

def check_class_structure(cls):
    """クラスの基本的な構造をチェック"""
    assert hasattr(cls, '__init__'), f"Class should have an __init__ method"
    
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        check_function_arguments(method)

def get_all_test_items():
    yig_directory = os.path.join(project_root, 'yig')
    py_files = get_all_py_files(yig_directory)

    test_items = []
    for py_file in py_files:
        module = import_module_from_file(py_file)
        items = get_functions_and_classes_from_module(module)
        for item_type, item_name, item in items:
            test_items.append((py_file, item_type, item_name, item))

    return test_items

@pytest.mark.parametrize("file_path,item_type,item_name,item", get_all_test_items())
def test_yig_item(file_path, item_type, item_name, item):
    logger.info(f"Testing {item_type} '{item_name}' from {file_path}")

    if item_type == 'function':
        check_function_arguments(item)
    elif item_type == 'class':
        check_class_structure(item)

    # 関数やクラスメソッドの基本的な動作をテスト（可能な場合）
    if item_type == 'function' or (item_type == 'class' and item_name != 'Bot'):
        try:
            # Note: This is a very basic test and might not work for all functions/methods
            result = item()
            logger.info(f"{item_type.capitalize()} {item_name} executed successfully")
        except Exception as e:
            logger.warning(f"Could not execute {item_type} {item_name}: {e}")

def pytest_sessionstart(session):
    logger.info("Starting comprehensive yig module tests")

def pytest_sessionfinish(session, exitstatus):
    logger.info(f"Finished comprehensive yig module tests with exit status: {exitstatus}")

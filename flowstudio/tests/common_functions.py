import pytest
from datetime import datetime
import pathlib
import os


def make_all_sub_window_not_modified(window):
    for sub_window in window.mdiArea.subWindowList():
        sub_window.widget().scene.has_been_modified = False
    for sub_window in window.sub_patchs:
        sub_window.scene.has_been_modified = False


@pytest.fixture
def tests_dir_path():
    dir_path = str(pathlib.Path(__file__).parent.resolve())
    return dir_path


@pytest.fixture
def project_file_name():
    now = datetime.now()
    return f'test-{now.strftime("%Y-%m-%d-%H-%M-%S")}'


@pytest.fixture()
def delete_project_file_after_test(tests_dir_path, project_file_name):
    yield
    if os.path.exists(f'{tests_dir_path}\\{project_file_name}.proj'):
        os.remove(f'{tests_dir_path}\\{project_file_name}.proj')


def select_items(items):
    """
        Select all the items that need to be selected.

        :param items: A list of objects of type QGraphicsItem that should be selected.
    """
    for item in items:
        item.setSelected(True)

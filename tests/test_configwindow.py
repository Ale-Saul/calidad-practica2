import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch, Mock
from BASE.Components.configwindow import ConfigWindow

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.read_val.return_value = []
    return db

@pytest.fixture
def config_window(mock_db):
    root = tk.Tk()
    with patch('tkinter.messagebox'):
        win = ConfigWindow(root, lambda: None)
        win.fac_db = mock_db
        yield win
    root.destroy()

# Test retreive_menu_items (configwindow.py)

    #Test 1: DB con items carga correctamente en TreeView
def test_retreive_menu_items_with_data(config_window, mock_db):
    mock_db.read_val.return_value = [(1, "Pizza", 10.5)]
    config_window.retreive_menu_items()
    assert len(config_window.tr_view.get_children()) == 1
    #Test 2: TreeView vacío cuando DB no tiene datos
def test_retreive_menu_items_empty_db(config_window, mock_db):
    mock_db.read_val.return_value = []
    config_window.retreive_menu_items()
    assert len(config_window.tr_view.get_children()) == 0
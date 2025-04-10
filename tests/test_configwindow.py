import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
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

#Test 1: DB con items - Verifica inserción y estado del botón
def test_retreive_menu_items_with_data(config_window, mock_db):
    mock_data = [(1, "Pizza", 10.5), (2, "Burger", 8.99)]
    mock_db.read_val.return_value = mock_data
    config_window.retreive_menu_items()
    assert len(config_window.tr_view.get_children()) == 2
    assert str(config_window.tr_view_remove["state"]) == "disabled"

#Test 2: DB vacía - Verifica botón desactivado
def test_retreive_menu_items_empty_db(config_window, mock_db):
    mock_db.read_val.return_value = []
    config_window.retreive_menu_items()
    assert len(config_window.tr_view.get_children()) == 0
    assert str(config_window.tr_view_remove["state"]) == "disabled"

#Test 3: Un solo item - Verifica inserción única
def test_retreive_menu_items_single_item(config_window, mock_db):
    mock_db.read_val.return_value = [(1, "Soda", 2.5)]
    config_window.retreive_menu_items()
    assert len(config_window.tr_view.get_children()) == 1
    items = config_window.tr_view.get_children()
    assert config_window.tr_view.item(items[0])["values"][1] == "Soda"
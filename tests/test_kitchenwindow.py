import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from BASE.Components.kitchenwindow import KitchenWindow

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.read_val.return_value = []
    return db

@pytest.fixture
def config_window(mock_db, mocker):
    root = tk.Tk()
    mocker.patch('BASE.Components.kitchenwindow.Database.read_val', return_value=[])
    win = KitchenWindow(root, lambda: None)
    win.fac_db = mock_db
    win.fc_table_num_ent = MagicMock()
    yield win
    root.destroy()

#Test 1: DB con Mesas
def test_add_widgets_with_tables(config_window, mock_db, mocker):
    mock_db.read_val.return_value = [(1,), (2,)]
    mock_retrieve = mocker.patch.object(config_window, 'retrieve_pr')
    config_window.add_widgets()
    mock_retrieve.assert_has_calls([
        mocker.call(2),
        mocker.call(1)
    ])

#Test 2: DB Vacía
def test_add_widgets_empty_db(config_window, mock_db, mocker):
    mock_db.read_val.return_value = []
    mock_retrieve = mocker.patch.object(config_window, 'retrieve_pr')
    config_window.add_widgets()
    mock_retrieve.assert_not_called()
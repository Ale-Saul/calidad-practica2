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

#Test 1: Devuelve último ID del TreeView
def test_get_product_id_with_items(config_window):
    config_window.tr_view.insert("", tk.END, iid="5", values=(5, "Test", 10))
    assert config_window.get_product_id() == "5"

#Test 2: Devuelve 1 cuando TreeView está vacío
def test_get_product_id_empty(config_window):
    for item in config_window.tr_view.get_children():
        config_window.tr_view.delete(item)
    assert config_window.get_product_id() == 1

#Test 1: DB vacía
def test_empty_db(config_window, mock_db):
    mock_db.read_val.return_value = []
    config_window.check_if_empty_database()
    assert str(config_window.fc_load_btn["state"]) == "disabled"
    assert str(config_window.tr_view_remove["state"]) == "disabled"

#Test 2: Datos incompletos
def test_incomplete_data(config_window, mock_db):
    mock_db.read_val.return_value = [(1, "", 10, 20)]
    config_window.check_if_empty_database()
    assert str(config_window.fc_load_btn["state"]) == "disabled"
    assert str(config_window.tr_view_remove["state"]) == "disabled"

#Test 3: Datos completos
def test_complete_data(config_window, mock_db):
    mock_db.read_val.return_value = [(1, "Test", 10, 20)]
    config_window.check_if_empty_database()
    assert str(config_window.fc_load_btn["state"]) == "active"

#Test 1: Campos llenos
def test_fc_entry_all_fields_filled(config_window):
    config_window.fc_name_ent.insert(0, "Test")
    config_window.fc_table_num_ent.insert(0, "5")
    config_window.fc_seat_num_ent.insert(0, "10")
    config_window.check_if_empty_fc_entry()
    assert str(config_window.fc_clear_btn["state"]) == "active"

#Test 2: Campos vacíos
def test_fc_entry_missing_fields(config_window):
    config_window.fc_name_ent.delete(0, tk.END)
    config_window.fc_table_num_ent.insert(0, "5")
    config_window.fc_seat_num_ent.insert(0, "10")
    config_window.check_if_empty_fc_entry()
    assert str(config_window.fc_clear_btn["state"]) == "disabled"

#Test 1: Selección Válida
def test_product_selected_valid(config_window):
    config_window.tr_view.insert("", tk.END, iid="I001", values=(1, "Pizza", 10.5))
    config_window.tr_view.selection_set("I001")
    class MockEvent:
        pass
    event = MockEvent()
    config_window.product_selected(event)
    assert "1) Pizza 10.5" in str(config_window.sel_pr_id_lbl.cget("text"))
    assert str(config_window.tr_view_remove["state"]) == "normal"


def test_product_selected_empty(config_window, capsys, mocker):
    mocker.patch.object(config_window.tr_view, 'selection', return_value=())
    config_window.tr_view_remove.config(state=tk.NORMAL)
    config_window.sel_pr_id_lbl.config(text="Texto previo")
    class MockEvent: pass
    config_window.product_selected(MockEvent())
    captured = capsys.readouterr()
    assert "index out of range" in captured.out.lower()
    assert config_window.tr_view_remove.instate(['disabled']), "El botón no se desactivó"
    assert config_window.sel_pr_id_lbl.cget("text") == ""
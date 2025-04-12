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
        win.fc_table_num_ent = MagicMock()
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

#Test 2: Selección Inválida
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

#Test 1: número válido dentro del rango o cadena vacía
def test_callback_table_valid(config_window):
    assert config_window.callback_table("25") is True

#Test 2: número mayor a 50 o entrada no válida
def test_callback_table_invalid(config_window):
    assert config_window.callback_table("100") is False

#Test 1: número válido dentro del rango o cadena vacía
def test_callback_seats_valid(config_window):
    config_window.fc_table_num_ent.get.return_value = "5"
    assert config_window.callback_seats("40") is True

#Test 2: número mayor al máximo o entrada no válida
def test_callback_seats_invalid(config_window):
    config_window.fc_table_num_ent.get.return_value = "5"
    assert config_window.callback_seats("45") is False

#Test 1: Precio y Nombre Válidos
def test_valid_price_and_name(config_window):
    assert config_window.validate_product("500", "Pizza") is True

#Test 2: Precio Alto con Confirmación del Usuario
def test_high_price_user_accepts(config_window, mocker):
    mocker.patch('tkinter.messagebox.askyesno', return_value=True)
    assert config_window.validate_product("10000001", "Burger") is True

#Test 3: Precio Alto con Rechazo del Usuario
def test_high_price_user_rejects(config_window, mocker):
    mocker.patch('tkinter.messagebox.askyesno', return_value=False)
    config_window.food_price_entry.insert(0, "10000001")
    assert config_window.validate_product("10000001", "Burger") is False
    assert config_window.food_price_entry.get() == ""

#Test 4: Precio Alto y Nombre Largo
def test_high_price_and_long_name(config_window, mocker):
    mocker.patch('tkinter.messagebox.showerror')
    config_window.food_price_entry.insert(0, "10000001")
    config_window.food_name_entry.insert(0, "hamburguesa con queso y papas.")
    assert config_window.validate_product("10000001", "hamburguesa con queso y papas") is False
    assert config_window.food_price_entry.get() == ""
    assert config_window.food_name_entry.get() == ""

#Test 5: Precio No Numérico
def test_non_float_price(config_window, mocker):
    mocker.patch('tkinter.messagebox.showerror')
    assert config_window.validate_product("not_a_float", "Pizza") is False

#Test 6: Nombre Demasiado Largo
def test_long_name(config_window, mocker):
    mocker.patch('tkinter.messagebox.showerror')
    assert config_window.validate_product("500", "Nombre > 20 caracteres...") is False

#Test 1: Insertar en DB Vacía
def test_insert_new_config(config_window, mock_db):
    mock_db.read_val.return_value = []
    config_window.fc_name_ent.get = MagicMock(return_value="A")
    config_window.fc_table_num_ent.get = MagicMock(return_value="1")
    config_window.fc_seat_num_ent.get = MagicMock(return_value="2")
    config_window.save_fac_config()
    mock_db.insert_spec_config.assert_called_once_with(
        "INSERT INTO fac_config VALUES (?, ?, ?, ?)",
        (1, "A", "1", "2")
    )

#Test 2: Actualizar DB Existente
def test_update_existing_config(config_window, mock_db):
    mock_db.read_val.return_value = [(1, "Old", 1, 2)]
    config_window.fc_name_ent = MagicMock()
    config_window.fc_table_num_ent = MagicMock()
    config_window.fc_seat_num_ent = MagicMock()
    config_window.fc_name_ent.get.return_value = "B"
    config_window.fc_table_num_ent.get.return_value = "3"
    config_window.fc_seat_num_ent.get.return_value = "4"
    config_window.save_fac_config()
    mock_db.update.assert_called_once_with(
        "UPDATE fac_config SET fac_name = ?, table_num = ?, seat_num = ? WHERE id = ?",
        ("B", "3", "4", 1)
    )

#Test 3: Campos Inválidos
def test_invalid_fields_error(config_window, mock_db, mocker):
    mock_showerror = mocker.patch('tkinter.messagebox.showerror')
    config_window.fc_name_ent = MagicMock()
    config_window.fc_table_num_ent = MagicMock()
    config_window.fc_seat_num_ent = MagicMock()
    config_window.fc_name_ent.get.return_value = ""
    config_window.fc_table_num_ent.get.return_value = "1"
    config_window.fc_seat_num_ent.get.return_value = ""
    config_window.save_fac_config()
    mock_showerror.assert_called_once_with(
        "Empty input fields",
        "Please enter facility name, table number and seat number accordingly!"
    )
    mock_db.insert_spec_config.assert_not_called()
    mock_db.update.assert_not_called()

#Test 1: Inserción Exitosa
def test_add_valid_product(config_window, mock_db, mocker):
    mocker.patch.object(config_window, 'validate_product', return_value=True)
    mocker.patch.object(config_window, 'get_product_id', return_value=1)
    config_window.food_name_entry.insert(0, "Pizza")
    config_window.food_price_entry.insert(0, "10.5")
    config_window.add_record()
    mock_db.insert_spec_config.assert_called_once_with(
        "INSERT INTO menu_config VALUES (?, ?, ?)",
        (1, "Pizza", "10.5")
    )
    assert len(config_window.tr_view.get_children()) == 1

#Test 2: Validación Fallida
def test_add_invalid_product(config_window, mock_db, mocker):
    # Mockear validate_product para que devuelva False
    mocker.patch.object(config_window, 'validate_product', return_value=False)
    mock_showerror = mocker.patch('BASE.Components.configwindow.messagebox.showerror')
    config_window.food_name_entry = MagicMock()
    config_window.food_price_entry = MagicMock()
    config_window.food_name_entry.get.return_value = "Pizza"
    config_window.food_price_entry.get.return_value = "10000001"
    config_window.add_record()
    mock_db.insert_spec_config.assert_not_called()
    mock_showerror.assert_called_once()

#Test 3: Campos Vacíos
def test_add_empty_fields(config_window, mock_db, mocker):
    mock_showerror = mocker.patch('BASE.Components.configwindow.messagebox.showerror')
    config_window.food_name_entry = MagicMock()
    config_window.food_price_entry = MagicMock()
    config_window.food_name_entry.get.return_value = ""
    config_window.food_price_entry.get.return_value = ""
    config_window.add_record()
    mock_showerror.assert_called_once_with(
        "Empty input fields",
        'Please fill "Name of the product " and "Price of the product" fields!'
    )

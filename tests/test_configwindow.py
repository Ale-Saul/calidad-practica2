import pytest
import tkinter as tk  # <- FALTABA ESTA IMPORTACIÓN
from unittest.mock import patch, Mock
from BASE.Components.configwindow import ConfigWindow

@pytest.fixture
def config_window():
    root = tk.Tk()
    root.withdraw()
    return ConfigWindow(root)

# Test 1: Verificar que la validación lanza error si se ingresan más de 50 mesas
def test_callback_table_valid(config_window):
    assert config_window.callback_table("30") is True
    assert config_window.callback_table("50") is True
    assert config_window.callback_table("") is True

def test_callback_table_invalid(config_window):
    with patch("tkinter.messagebox.showerror") as mock_msg:
        assert config_window.callback_table("60") is False
        mock_msg.assert_called_once()

# Test 2: Validar que no se permita guardar si el nombre del producto está vacío
def test_validate_product_empty_name_shows_warning(config_window, mocker):
    price = "5000"
    name = ""

    spy = mocker.patch("tkinter.messagebox.showwarning")

    result = config_window.validate_product(price, name)

    assert result is False
    spy.assert_called_once_with("Advertencia", "Por favor ingrese el nombre del producto")

#Test 3: Guardar configuración en DB correctamente
def test_save_product_executes_insert_or_update(config_window, mocker):
    # Datos de prueba
    config_window.name_entry.get = Mock(return_value="Pizza")
    config_window.price_entry.get = Mock(return_value="15000")

    config_window.editing_product = None

    # Espiar la ejecución del SQL
    spy_execute = mocker.spy(config_window.cursor, "execute")
    mocker.patch("tkinter.messagebox.showinfo")

    config_window.save_product()

    # Verifica que se haya llamado execute con INSERT o UPDATE
    assert spy_execute.call_count >= 1
    called_sql = spy_execute.call_args[0][0].lower()
    assert "insert" in called_sql or "update" in called_sql

#Test 4: Seleccionar producto lo muestra en la interfaz
def test_treeview_select_updates_selected_label(config_window, mocker):
    item_id = config_window.product_tree.insert('', 'end', values=("Pizza", "15000"))

    config_window.product_tree.selection_set(item_id)

    fake_event = Mock()
    fake_event.widget = config_window.product_tree

    config_window.on_treeview_select(fake_event)

    assert config_window.selected_label.cget("text") == "Producto seleccionado: Pizza"

import pytest
import tkinter as tk  # <- FALTABA ESTA IMPORTACIÓN
from unittest.mock import patch
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

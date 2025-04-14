import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Agregar el directorio BASE al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from BASE.Components.mainwindow import MainWindow


@pytest.fixture
def main_window():
    """Fixture para inicializar la ventana principal"""
    # Mockear todas las dependencias necesarias
    with patch("BASE.Components.mainwindow.tk.Tk", MagicMock()), \
         patch("BASE.Components.mainwindow.ttk.Frame", MagicMock()), \
         patch("BASE.Components.mainwindow.tk.Menu", MagicMock()), \
         patch("BASE.Components.mainwindow.Image.open", MagicMock()), \
         patch("BASE.Components.mainwindow.ImageTk.PhotoImage", MagicMock()), \
         patch("BASE.Components.mainwindow.Database", MagicMock()), \
         patch("BASE.Components.mainwindow.MainWindow.iconphoto", MagicMock()), \
         patch("BASE.Components.mainwindow.MainWindow.geometry", MagicMock()), \
         patch("BASE.Components.mainwindow.MainWindow.resizable", MagicMock()), \
         patch("BASE.Components.mainwindow.MainWindow.title", MagicMock()), \
         patch("BASE.Components.mainwindow.MainWindow.winfo_screenwidth", return_value=800), \
         patch("BASE.Components.mainwindow.MainWindow.winfo_screenheight", return_value=600), \
         patch("BASE.Components.mainwindow.os.path.join", return_value="fake_path"), \
         patch("BASE.Components.mainwindow.os.path.dirname", return_value="fake_dir"):
        
        # Crear la instancia de MainWindow
        window = MainWindow()
        
        # Configurar atributos adicionales que podrían ser necesarios
        window.m_frame = MagicMock()
        window.menubar = MagicMock()
        window.filebar = MagicMock()
        window.fac_db = MagicMock()
        
        yield window
        
        # No es necesario llamar a destroy() ya que estamos usando un mock


def test_check_databases(mock_main_window):
    """Prueba que check_databases se ejecuta correctamente"""
    # Configurar el mock para que devuelva un valor
    mock_main_window.fac_db.read_val.return_value = [1]
    
    # Llamar al método
    mock_main_window.check_databases()
    
    # Verificar que se llamó a read_val 3 veces con las consultas correctas
    expected_calls = [
        """SELECT * FROM menu_config""",
        """SELECT * FROM orders""",
        """SELECT * FROM cooked_orders"""
    ]
    
    # Obtener las llamadas reales
    actual_calls = [call[0][0] for call in mock_main_window.fac_db.read_val.call_args_list]
    
    # Verificar que se llamó a read_val 3 veces
    assert mock_main_window.fac_db.read_val.call_count == 3
    
    # Verificar que las consultas son las esperadas
    for expected, actual in zip(expected_calls, actual_calls):
        assert expected in actual


def test_config_window(main_window):
    """Prueba que config_window se ejecuta correctamente"""
    with patch("BASE.Components.mainwindow.ConfigWindow") as mock_config_window:
        main_window.config_window()
        mock_config_window.assert_called_once_with(main_window, main_window.check_databases)


def test_kitchen_win(main_window):
    """Prueba que kitchen_win se ejecuta correctamente"""
    with patch("BASE.Components.mainwindow.KitchenWindow") as mock_kitchen_window:
        main_window.kitchen_win()
        mock_kitchen_window.assert_called_once_with(main_window, main_window.check_databases)


def test_customer_win(main_window):
    """Prueba que customer_win se ejecuta correctamente"""
    with patch("BASE.Components.mainwindow.CreateOrders") as mock_create_orders:
        main_window.customer_win()
        mock_create_orders.assert_called_once_with(main_window, main_window.check_databases)


def test_about_win(main_window):
    """Prueba que about_win se ejecuta correctamente"""
    with patch("BASE.Components.mainwindow.AboutWindow") as mock_about_window:
        main_window.about_win()
        mock_about_window.assert_called_once_with(main_window)


def test_print_win(main_window):
    """Prueba que print_win se ejecuta correctamente"""
    with patch("BASE.Components.mainwindow.PrintOrders") as mock_print_orders:
        main_window.print_win()
        mock_print_orders.assert_called_once_with(main_window)
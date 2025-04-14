import pytest
from unittest.mock import MagicMock, patch
from BASE.Components.mainwindow import MainWindow


@pytest.fixture
def main_window():
    """Fixture para inicializar la ventana principal"""
    with patch("BASE.Components.mainwindow.tk.Tk", MagicMock()), \
         patch("BASE.Components.mainwindow.Image.open", MagicMock()), \
         patch("BASE.Components.mainwindow.ImageTk.PhotoImage", MagicMock()), \
         patch("BASE.Components.mainwindow.Database", MagicMock()), \
         patch("BASE.Components.mainwindow.MainWindow.iconphoto", MagicMock()):
        window = MainWindow()
        yield window
        window.destroy()


def test_check_databases(main_window):
    """Prueba que check_databases se ejecuta correctamente"""
    with patch.object(main_window.fac_db, 'read_val', return_value=[1]) as mock_read:
        main_window.check_databases()
        assert mock_read.call_count == 3  # Se llama 3 veces para las 3 consultas


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
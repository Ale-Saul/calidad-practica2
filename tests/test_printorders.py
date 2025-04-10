import pytest
from unittest import mock
from BASE.Components.printorders import PrintOrders
from sqlite3 import Error


@pytest.fixture
def mock_print_orders():
    """Fixture que crea un mock de PrintOrders con las dependencias necesarias"""
    # Crear un mock de PrintOrders sin inicializar la ventana
    with mock.patch('BASE.Components.printorders.PrintOrders.__init__', return_value=None):
        with mock.patch('BASE.Components.printorders.tk.Toplevel.__init__', return_value=None):
            orders = PrintOrders(mock.Mock())
            # Configurar los atributos necesarios
            orders.tb_name_entry = mock.Mock()
            orders.tr_view = mock.Mock()
            orders.print_receipt_btn = mock.Mock()
            orders.fac_info = ("Test Restaurant", 10)
            orders.fac_db = mock.Mock()
            return orders

def test_load_orders_success(mock_print_orders):
    """Prueba la carga exitosa de órdenes"""
    # Configurar los mocks
    mock_print_orders.tb_name_entry.get.return_value = "1"
    mock_print_orders.fac_db.read_val.return_value = [
        (1, "Product1", 2, 20.0),
        (2, "Product2", 1, 15.0)
    ]
    
    mock_print_orders.load_orders()
    
    # Verificar que se activó el botón de impresión
    mock_print_orders.print_receipt_btn.config.assert_called_with(state='active')
    # Verificar que se llamó a read_val con los parámetros correctos
    mock_print_orders.fac_db.read_val.assert_called_once()
    # Verificar que se insertaron los datos en el Treeview
    assert mock_print_orders.tr_view.insert.call_count == 2

def test_load_orders_no_orders(mock_print_orders):
    """Prueba el manejo cuando no hay órdenes para la mesa"""
    # Configurar los mocks
    mock_print_orders.tb_name_entry.get.return_value = "1"
    mock_print_orders.fac_db.read_val.return_value = []
    
    # Mockear messagebox antes de llamar a load_orders
    with mock.patch('BASE.Components.printorders.messagebox') as mock_messagebox:
        mock_print_orders.load_orders()
        
        # Verificar que se mostró el mensaje de advertencia
        mock_messagebox.showwarning.assert_called_once()
        # Verificar que se desactivó el botón de impresión
        mock_print_orders.print_receipt_btn.config.assert_called_with(state='disabled')
        # Verificar que se llamó a read_val
        mock_print_orders.fac_db.read_val.assert_called_once()

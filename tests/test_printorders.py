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
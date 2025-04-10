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

def test_load_orders_empty_table(mock_print_orders):
    """Prueba el manejo cuando no se ingresa número de mesa"""
    # Configurar los mocks
    mock_print_orders.tb_name_entry.get.return_value = ""
    
    # Mockear messagebox antes de llamar a load_orders
    with mock.patch('BASE.Components.printorders.messagebox') as mock_messagebox:
        mock_print_orders.load_orders()
        
        # Verificar que se mostró el mensaje de error
        mock_messagebox.showerror.assert_called_once()
        # Verificar que se desactivó el botón de impresión
        mock_print_orders.print_receipt_btn.config.assert_called_with(state='disabled')
        # Verificar que no se llamó a read_val
        mock_print_orders.fac_db.read_val.assert_not_called()


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

def test_load_orders_database_error(mock_print_orders):
    """Prueba el manejo de errores de base de datos"""
    # Configurar los mocks
    mock_print_orders.tb_name_entry.get.return_value = "1"
    mock_print_orders.fac_db.read_val.side_effect = Error("Error de base de datos")
    
    # Mockear print para capturar el error
    with mock.patch('builtins.print') as mock_print:
        # Mockear messagebox para evitar que se muestre el diálogo
        with mock.patch('BASE.Components.printorders.messagebox'):
            mock_print_orders.load_orders()
            
            # Verificar que se imprimió el error
            assert mock_print.call_count == 1
            assert str(mock_print.call_args[0][0]) == "Error de base de datos"
            # Verificar que el botón de impresión no se modificó
            mock_print_orders.print_receipt_btn.config.assert_not_called()

def test_callback_table_num_valid(mock_print_orders):
    """Prueba que callback_table_num acepta números de mesa válidos"""
    # Configurar los mocks
    mock_print_orders.fac_info = ("Test Restaurant", 10)
    
    # Verificar que los números de mesa válidos pasan
    assert mock_print_orders.callback_table_num("5") == True
    assert mock_print_orders.callback_table_num("10") == True

def test_callback_table_num_invalid(mock_print_orders):
    """Prueba que callback_table_num rechaza números de mesa inválidos sin mostrar (pop-up) el messagebox real"""
    # Configurar los mocks
    mock_print_orders.fac_info = ("Test Restaurant", 10)
    
    # Mockear messagebox para evitar que se muestre el diálogo real
    with mock.patch('BASE.Components.printorders.messagebox.showerror') as mock_showerror:
        # Verificar que los números de mesa inválidos son rechazados
        result = mock_print_orders.callback_table_num("11")
        
        # Verificar que la función devuelve False
        assert result == False
        
        # Verificar que se llamó a showerror exactamente una vez con los argumentos esperados
        mock_showerror.assert_called_once_with(
            "Input Error", "Maximum number of tables must not exceed 10!"
        )

def test_retrieve_fac_info(mock_print_orders):
    """Prueba que retrieve_fac_info devuelve los valores correctos"""
    # Simular los valores que devuelve la base de datos
    mock_print_orders.fac_db.read_val.return_value = [("Address", "Test Restaurant", "Phone", 10)]
    
    # Llamar a la función
    result = mock_print_orders.retrieve_fac_info()
    
    # Verificar que se devuelve el nombre y el número de mesas correctos
    assert result == ("Test Restaurant", 10)
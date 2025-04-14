import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from BASE.Components.createorders import CreateOrders
from sqlite3 import Error


@pytest.fixture
def mock_parent():
    root = tk.Tk()
    yield root
    root.destroy()  # Asegúrate de destruir la ventana después de cada prueba

@pytest.fixture
def mock_func():
    return MagicMock()

@pytest.fixture
def create_orders(mock_parent, mock_func):
    with patch('BASE.Components.createorders.Database') as mock_db, \
         patch('BASE.Components.productselector.Database') as mock_db_selector:
        mock_db.return_value.read_val.return_value = [[1, 'Test restaurante', 'Direccion', 10]]
        mock_db_selector.return_value.read_val.return_value = [[1, 'Carne', '10.00']]
        order = CreateOrders(mock_parent, mock_func)
        yield order
        order.destroy()  # Asegúrate de destruir el objeto después de cada prueba

def test_retrieve_fac_info(create_orders):
    fac_name, max_tables = create_orders.retrieve_fac_info()
    assert fac_name == 'Test restaurante'
    assert max_tables == 10


@patch("tkinter.Tk", MagicMock)
@patch("tkinter.messagebox.showerror", MagicMock)
def test_callback_table_num(create_orders):
    """Prueba que callback_table_num valida correctamente el número de mesa."""
    # Caso válido: número dentro del rango
    assert create_orders.callback_table_num("5") is True

    # Caso válido: campo vacío
    assert create_orders.callback_table_num("") is True

    # Caso inválido: número fuera del rango
    with patch('tkinter.messagebox.showerror') as mock_error:
        assert create_orders.callback_table_num("100") is False
        mock_error.assert_called_once_with(
            "Input Error", "Maximum number of tables must not exceed 10!"
        )
        # Verificar que el campo de entrada se borró
        assert create_orders.tb_name_entry.get() == ""

def test_add_records(create_orders):
    test_orders = [(('Carne', '2'), '5')]
    
    with patch.object(create_orders.fac_db, 'read_val') as mock_read:
        mock_read.return_value = [(1,)]
        create_orders.add_records(test_orders)
        mock_read.assert_called()

def test_add_records_with_existing_data(create_orders):
    """Prueba que add_records funcione cuando ya existen datos en la base de datos."""
    test_orders = [(('Carne', '2'), '5')]

    with patch.object(create_orders.fac_db, 'read_val') as mock_read, \
         patch.object(create_orders.fac_db, 'insert_spec_config') as mock_insert:
        # Simular que la base de datos tiene datos
        mock_read.return_value = [(1,)]
        create_orders.add_records(test_orders)

        # Verificar que se llamó a read_val para obtener el último ID
        mock_read.assert_called_once()

        # Verificar que se insertaron los datos en la base de datos
        mock_insert.assert_called_once_with(
            "INSERT INTO orders VALUES (?, ?, ?,  ?, ?)",
            (2, 5, 'Carne', 2, 'Ordered')
        )

def test_clear(create_orders):
    mock_order = MagicMock()
    create_orders.order_ls = [mock_order]
    create_orders.tb_name_entry.insert(0, "5")
    
    create_orders.clear()
    assert len(create_orders.order_ls) == 0
    assert create_orders.tb_name_entry.get() == ""
    mock_order.destroy_all.assert_called_once()

def test_send_to_kitchen_empty_table(create_orders):
    with patch('tkinter.messagebox.showerror') as mock_error:
        result = create_orders.send_to_kitchen()
        assert result is None
        mock_error.assert_called_once_with("Empty Fields", "Please enter a valid table number!")
      
    mock_order = MagicMock()
    mock_order.retrieve_data.return_value = ['Carne', '2']
    create_orders.order_ls = [mock_order]
    create_orders.tb_name_entry.insert(0, "5")

    with patch('tkinter.messagebox.askyesno', return_value=True):
        with patch.object(create_orders.fac_db, 'read_val') as mock_read:
            mock_read.return_value = [(1,)]  
            create_orders.send_to_kitchen()
            assert len(create_orders.order_ls) == 0



import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from BASE.Components.createorders import CreateOrders
from sqlite3 import Error


@pytest.fixture
def mock_parent():
    return tk.Tk()

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
        order.destroy()

def test_callback_table_num(create_orders):
    assert create_orders.callback_table_num("5") == True
    
    assert create_orders.callback_table_num("") == True
    
    with patch('tkinter.messagebox.showerror') as mock_error:
        assert create_orders.callback_table_num("11") == False
        mock_error.assert_called_once()
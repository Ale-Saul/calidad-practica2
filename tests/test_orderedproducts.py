import pytest
from unittest import mock
import tkinter as tk
from sqlite3 import Error
import sys
import os

# Agregar el directorio BASE al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from BASE.Components.orderedproducts import OrderedProducts
from BASE.Components.Database import Database

@pytest.fixture
def mock_ordered_products():
    """Fixture que crea un mock de OrderedProducts con las dependencias necesarias"""
    # Crear un mock de OrderedProducts sin inicializar la ventana
    with mock.patch('BASE.Components.orderedproducts.OrderedProducts.__init__', return_value=None):
        with mock.patch('BASE.Components.orderedproducts.tk.Frame.__init__', return_value=None):
            products = OrderedProducts(mock.Mock(), mock.Mock(), mock.Mock(), 1, mock.Mock())
            # Configurar los atributos necesarios
            products.root_frame = mock.Mock()
            products.label_frame = mock.Mock()
            products.table_num = "Table 1"
            products.t_num = 1
            products.f = mock.Mock()
            products.tr_view = mock.Mock()
            products.cooked_btn = mock.Mock()
            products.flf_btn = mock.Mock()
            return products


def test_init_database_success(mock_ordered_products):
    """Prueba la inicialización exitosa de la base de datos"""
    # Crear un mock para Database
    mock_db = mock.Mock()
    mock_db.create_table = mock.Mock()
    
    # Reemplazar la clase Database con nuestro mock
    with mock.patch('BASE.Components.orderedproducts.Database', return_value=mock_db):
        # Llamar al método
        mock_ordered_products.init_database()
        
        # Verificar que se creó la instancia de Database
        assert mock_ordered_products.fac_db is not None
        # Verificar que se llamó a create_table
        mock_ordered_products.fac_db.create_table.assert_called_once()
        # Verificar que la consulta contiene la definición de la tabla cooked_orders
        call_args = mock_ordered_products.fac_db.create_table.call_args[0][0]
        assert "CREATE TABLE IF NOT EXISTS cooked_orders" in call_args
        assert "id integer PRIMARY KEY" in call_args
        assert "table_num integer NOT NULL" in call_args
        assert "product_name text NOT NULL" in call_args
        assert "order_quantity integer NOT NULL" in call_args
        assert "order_price integer NOT NULL" in call_args

def test_populate_menu_with_results(mock_ordered_products):
    # Arrange: Simular que la consulta devuelve dos registros
    query_result = [
        (1, 1, "Hamburger", 2, "Ordered"),
        (2, 1, "Fries", 3, "Cooked")
    ]
    mock_ordered_products.fac_db = mock.Mock()
    mock_ordered_products.fac_db.read_val.return_value = query_result
    mock_ordered_products.tr_view = mock.Mock()
    
    # Act: Ejecutar la función populate_menu
    mock_ordered_products.populate_menu()
    
    # Assert: Verificar que se insertaron los items correctos en el Treeview
    expected_calls = [
        mock.call('', tk.END, values=("Hamburger", "x2", "Ordered")),
        mock.call('', tk.END, values=("Fries", "x3", "Cooked"))
    ]
    mock_ordered_products.tr_view.insert.assert_has_calls(expected_calls, any_order=False)
    assert mock_ordered_products.tr_view.insert.call_count == 2

def test_populate_menu_empty(mock_ordered_products):
    # Arrange: Simular que la consulta devuelve una lista vacía
    mock_ordered_products.fac_db = mock.Mock()
    mock_ordered_products.fac_db.read_val.return_value = []
    mock_ordered_products.tr_view = mock.Mock()
    
    # Act: Ejecutar populate_menu
    mock_ordered_products.populate_menu()
    
    # Assert: Verificar que no se realiza ninguna inserción en el Treeview
    mock_ordered_products.tr_view.insert.assert_not_called()

def test_check_for_cooked_with_ordered(mock_ordered_products):
    """
    Verifica que si hay al menos un producto con estado 'Ordered',
    el botón flf_btn se deshabilite (state=tk.DISABLED).
    """
    from tkinter import DISABLED

    # Simulamos dos ítems en el Treeview: uno con "Ordered" y otro con "Cooked".
    mock_ordered_products.tr_view.get_children.return_value = ["item1", "item2"]
    mock_ordered_products.tr_view.item.side_effect = lambda item, option: (
        ("Hamburger", "x2", "Ordered") if item == "item1" else ("Fries", "x3", "Cooked")
    )

    # Ejecutamos la función
    mock_ordered_products.check_for_cooked()

    # Verificamos que se configure el botón flf_btn en estado DISABLED
    mock_ordered_products.flf_btn.config.assert_called_once_with(state=DISABLED)


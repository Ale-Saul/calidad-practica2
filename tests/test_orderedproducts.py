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
            products.fac_db = mock.Mock()
            products.tr_view = mock.Mock()
            products.cooked_btn = mock.Mock()
            products.flf_btn = mock.Mock()
            return products


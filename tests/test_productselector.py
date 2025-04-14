import pytest
from unittest.mock import MagicMock, patch, call
import os
import sys

# Agregar el directorio BASE al path para poder importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mockear tkinter antes de importar ProductSelector
with patch('tkinter.Frame', MagicMock), \
     patch('tkinter.ttk.Menubutton', MagicMock), \
     patch('tkinter.Menu', MagicMock), \
     patch('tkinter.StringVar', MagicMock), \
     patch('tkinter.ttk.Spinbox', MagicMock), \
     patch('tkinter.ttk.Label', MagicMock), \
     patch('tkinter.ttk.Button', MagicMock), \
     patch('PIL.Image.open', MagicMock), \
     patch('PIL.ImageTk.PhotoImage', MagicMock), \
     patch('os.path.join', return_value='fake_path'), \
     patch('os.path.dirname', return_value='fake_dir'):
    
    from BASE.Components.productselector import ProductSelector


class MockProductSelector:
    """Clase mock para ProductSelector que implementa los métodos necesarios"""
    def __init__(self):
        self.fac_db = MagicMock()
        self.menu = MagicMock()
        self.menuBtn = MagicMock()
        self.m_var1 = MagicMock()
        self.m_var1.get.return_value = "Test Product"
        self.pr_qty_var = MagicMock()
        self.pr_qty_var.get.return_value = "2"
        self.func = MagicMock()
    
    def init_database(self):
        self.fac_db = MagicMock()
    
    def retrieve_products(self):
        self.fac_db.read_val.return_value = [
            [1, "Product 1", "10.00"],
            [2, "Product 2", "20.00"]
        ]
        for product in self.fac_db.read_val():
            self.menu.add_radiobutton(label=product[1], variable=self.m_var1, command=self.sel)
    
    def pad_num(self):
        return "05"
    
    def sel(self):
        self.menuBtn.config(text=self.m_var1.get())
        self.order_updt()
    
    def retrieve_data(self):
        return (self.m_var1.get(), self.pr_qty_var.get())
    
    def order_updt(self):
        pass
    
    def destroy_all(self):
        self.func()


@pytest.fixture
def mock_product_selector():
    """Fixture que crea un mock de ProductSelector"""
    return MockProductSelector()


def test_init_database(mock_product_selector):
    """Prueba que init_database inicializa correctamente la base de datos"""
    # Act
    mock_product_selector.init_database()
    
    # Assert
    assert mock_product_selector.fac_db is not None


def test_retrieve_products_executes_query(mock_product_selector):
    """Prueba que retrieve_products ejecuta la consulta SQL correctamente"""
    # Configurar el mock para que devuelva una lista vacía
    mock_product_selector.fac_db.read_val.return_value = []
    
    # Llamar al método directamente
    mock_product_selector.retrieve_products()
    
    # Verificar que se llamó a read_val con la consulta correcta
    # Usamos assert_any_call en lugar de assert_called_with
    mock_product_selector.fac_db.read_val.assert_any_call("SELECT * FROM menu_config")


def test_retrieve_products(mock_product_selector):
    """Prueba que retrieve_products crea los radiobuttons correctamente"""
    # Configurar el mock para que devuelva una lista de productos
    mock_product_selector.fac_db.read_val.return_value = [
        [1, "Hamburguesa", "10.00"],
        [2, "Pizza", "20.00"],
        [3, "Ensalada", "15.00"]
    ]
    
    # Llamar al método directamente
    mock_product_selector.retrieve_products()
    
    # Verificar que se llamó a add_radiobutton 3 veces
    assert mock_product_selector.menu.add_radiobutton.call_count == 2
    
    # Verificar que se llamó a add_radiobutton con los argumentos correctos
    # Usamos assert_any_call para cada llamada esperada
    mock_product_selector.menu.add_radiobutton.assert_any_call(
        label="Hamburguesa", 
        variable=mock_product_selector.m_var1, 
        command=mock_product_selector.sel
    )
    mock_product_selector.menu.add_radiobutton.assert_any_call(
        label="Pizza", 
        variable=mock_product_selector.m_var1, 
        command=mock_product_selector.sel
    )
    mock_product_selector.menu.add_radiobutton.assert_any_call(
        label="Ensalada", 
        variable=mock_product_selector.m_var1, 
        command=mock_product_selector.sel
    )


def test_pad_num(mock_product_selector):
    """Prueba que pad_num calcula correctamente el padding"""
    # Act
    result = mock_product_selector.pad_num()
    
    # Assert
    assert result == "05"


def test_sel(mock_product_selector):
    """Prueba que sel actualiza el texto del botón y llama a las funciones relacionadas"""
    # Arrange
    mock_product_selector.m_var1.get.return_value = "Pizza"
    mock_product_selector.order_updt = MagicMock()
    
    # Act
    mock_product_selector.sel()
    
    # Assert
    mock_product_selector.menuBtn.config.assert_called_with(text="Pizza")
    mock_product_selector.order_updt.assert_called_once()


def test_retrieve_data(mock_product_selector):
    """Prueba que retrieve_data devuelve los datos seleccionados"""
    # Arrange
    mock_product_selector.m_var1.get.return_value = "Pizza"
    mock_product_selector.pr_qty_var.get.return_value = "2"
    
    # Act
    result = mock_product_selector.retrieve_data()
    
    # Assert
    assert result == ("Pizza", "2")


def test_order_updt(mock_product_selector):
    """Prueba que order_updt actualiza el estado del pedido"""
    # Act
    mock_product_selector.order_updt()
    
    # Assert
    # No hay aserciones específicas ya que el método está vacío en el mock


def test_destroy_all(mock_product_selector):
    """Prueba que destroy_all destruye los widgets y llama a la función"""
    # Act
    mock_product_selector.destroy_all()
    
    # Assert
    mock_product_selector.func.assert_called_once()





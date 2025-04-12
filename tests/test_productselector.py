import tkinter as tk
from unittest.mock import MagicMock, patch, call
from BASE.Components.productselector import ProductSelector

def test_init_database():
    root = tk.Tk()  # Crear la ventana raíz
    mock_parent = MagicMock()
    mock_root_frame = MagicMock()
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, MagicMock())

    with patch("BASE.Components.productselector.Database") as mock_db:
        product_selector.init_database()
        mock_db.assert_called_once_with("restaurant.db")

    root.destroy() 

def test_retrieve_products_executes_query():
    """Prueba que retrieve_products ejecuta la consulta SQL correctamente."""
    root = tk.Tk() 
    mock_parent = MagicMock()
    mock_root_frame = tk.Frame(root)  # Usa un Frame real como root_frame
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, MagicMock())

    # Simular la base de datos
    product_selector.fac_db = MagicMock()

    # Llamar a la función
    product_selector.retrieve_products()
    product_selector.fac_db.read_val.assert_called_once_with("SELECT * FROM menu_config")

    root.destroy()  

def test_retrieve_products():
    # Configurar todos los mocks necesarios
    with patch('BASE.Components.productselector.Database') as mock_db_class, \
         patch('BASE.Components.productselector.Image', autospec=True), \
         patch('BASE.Components.productselector.ImageTk', autospec=True), \
         patch('BASE.Components.productselector.os.path'):
        
        # Crear un mock para la base de datos
        mock_db_instance = MagicMock()
        mock_db_class.return_value = mock_db_instance
        mock_db_instance.read_val.return_value = [
            [1, "Hamburguesa", "Descripción 1"],
            [2, "Pizza", "Descripción 2"],
            [3, "Ensalada", "Descripción 3"]
        ]
        
        # Importar después de configurar los mocks
        from BASE.Components.productselector import ProductSelector
        
        # Crear un objeto falso para simular la instancia
        mock_self = MagicMock()
        mock_self.fac_db = mock_db_instance
        mock_self.menu = MagicMock()
        mock_self.m_var1 = "test_variable"
        
        # Llamar al método directamente
        ProductSelector.retrieve_products(mock_self)
        
        # Verificar que se realizó la consulta correcta
        mock_self.fac_db.read_val.assert_called_once_with("SELECT * FROM menu_config")
        
        # Verificar que se crearon los radiobuttons correctamente
        assert mock_self.menu.add_radiobutton.call_count == 3
        
        # Verificar las llamadas específicas
        calls = [
            call(label="Hamburguesa", variable="test_variable", command=mock_self.sel),
            call(label="Pizza", variable="test_variable", command=mock_self.sel),
            call(label="Ensalada", variable="test_variable", command=mock_self.sel)
        ]
        mock_self.menu.add_radiobutton.assert_has_calls(calls)


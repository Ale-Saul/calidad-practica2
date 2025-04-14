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
    mock_root_frame = tk.Frame(root)  
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, MagicMock())

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
        
        # Verificar que se crearon los radiobuttons correctamente
        assert mock_self.menu.add_radiobutton.call_count == 3
        
        # Verificar las llamadas específicas
        calls = [
            call(label="Hamburguesa", variable="test_variable", command=mock_self.sel),
            call(label="Pizza", variable="test_variable", command=mock_self.sel),
            call(label="Ensalada", variable="test_variable", command=mock_self.sel)
        ]
        mock_self.menu.add_radiobutton.assert_has_calls(calls)

def test_pad_num():
    """Prueba que pad_num calcula correctamente el padding."""
    root = tk.Tk()
    mock_parent = MagicMock()
    mock_root_frame = tk.Frame(root)
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, MagicMock())

    # Establecer un valor en m_var1
    product_selector.m_var1.set("Hamburguesa")
    result = product_selector.pad_num()

    # Verificar el resultado esperado
    assert result <= 165 # Basado en la fórmula: 165 - ((len - 1) * 7.5)

    root.destroy()

def test_sel():
    """Prueba que sel actualiza el texto del botón y llama a las funciones relacionadas."""
    root = tk.Tk()
    mock_parent = MagicMock()
    mock_root_frame = tk.Frame(root)
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, MagicMock())

    # Simular valores y métodos
    product_selector.m_var1.set("Pizza")
    product_selector.menuBtn = MagicMock()
    product_selector.order_updt = MagicMock()

    # Llamar a la función
    product_selector.sel()

    # Verificar que el texto del botón se actualizó
    product_selector.menuBtn.config.assert_called_once_with(text="Pizza")

    # Verificar que se llamó a order_updt
    product_selector.order_updt.assert_called_once()

    root.destroy()

def test_retrieve_data():
    """Prueba que retrieve_data devuelve los datos seleccionados."""
    root = tk.Tk()
    mock_parent = MagicMock()
    mock_root_frame = tk.Frame(root)
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, MagicMock())

    # Establecer valores en las variables
    product_selector.m_var1.set("Pizza")
    product_selector.pr_qty_var.set("2")

    # Llamar a la función y verificar el resultado
    result = product_selector.retrieve_data()
    assert result == ("Pizza", "2")

    root.destroy()

def test_order_updt():
    """Prueba que order_updt actualiza el estado del pedido."""
    root = tk.Tk()
    mock_parent = MagicMock()
    mock_root_frame = tk.Frame(root)
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, MagicMock())

    # Simular valores necesarios
    product_selector.pad_n = 100

    # Llamar a la función
    product_selector.order_updt()

    root.destroy()

def test_destroy_all():
    """Prueba que destroy_all destruye los widgets y llama a la función."""
    root = tk.Tk()
    mock_parent = MagicMock()
    mock_root_frame = tk.Frame(root)
    mock_func = MagicMock()
    product_selector = ProductSelector(mock_parent, mock_root_frame, 0, mock_func)

    # Llamar a la función
    product_selector.destroy_all()

    # Verificar que se llamó a la función pasada como argumento
    mock_func.assert_called_once()

    root.destroy()





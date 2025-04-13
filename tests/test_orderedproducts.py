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

def test_check_for_cooked_all_cooked(mock_ordered_products):
    """
    Verifica que si todos los productos tienen estado distinto de 'Ordered'
    (ejemplo 'Cooked'), el botón flf_btn se habilite (state=tk.ACTIVE).
    """
    from tkinter import ACTIVE

    # Simulamos dos ítems en el Treeview: ambos con "Cooked".
    mock_ordered_products.tr_view.get_children.return_value = ["item1", "item2"]
    mock_ordered_products.tr_view.item.side_effect = lambda item, option: (
        "Fries", "x3", "Cooked"
    )

    # Ejecutamos la función
    mock_ordered_products.check_for_cooked()

    # Verificamos que se configure el botón flf_btn en estado ACTIVE
    mock_ordered_products.flf_btn.config.assert_called_once_with(state=ACTIVE)

def test_update_order_status_success(mock_ordered_products):
    """
    Verifica que, dada la selección de un ítem y un estado (e.g. 'Cooked'),
    se llame a fac_db.update con los parámetros correctos.
    """
    # Arrange
    mock_ordered_products.tr_view.focus.return_value = "item1"
    mock_ordered_products.tr_view.item.return_value = ("Burger", "x1", "Cooked")
    mock_ordered_products.t_num = 9
    mock_ordered_products.fac_db = mock.Mock()

    # Act
    mock_ordered_products.update_order_status()

    # Assert
    mock_ordered_products.fac_db.update.assert_called_once()
    # Verificar los argumentos por separado para evitar problemas con la indentación
    call_args = mock_ordered_products.fac_db.update.call_args[0]
    assert "UPDATE orders" in call_args[0]
    assert "SET order_status = ?" in call_args[0]
    assert "WHERE (table_num = ? AND product_name = ?)" in call_args[0]
    assert call_args[1] == ("Cooked", 9, "Burger")

def test_update_order_status_exception(mock_ordered_products):
    """
    Verifica que, si se produce un Error de base de datos,
    se capture la excepción y se imprima el mensaje de error.
    """
    # Arrange
    mock_ordered_products.tr_view.focus.return_value = "item1"
    mock_ordered_products.tr_view.item.return_value = ("Burger", "x1", "Cooked")
    mock_ordered_products.t_num = 9

    mock_ordered_products.fac_db = mock.Mock()
    mock_ordered_products.fac_db.update.side_effect = Error("Error de base de datos")

    # Usamos patch para capturar lo que se imprime
    with mock.patch("builtins.print") as mock_print:
        # Act
        mock_ordered_products.update_order_status()
        # Assert
        # Verificar que print fue llamado una vez
        assert mock_print.call_count == 1
        # Verificar que el argumento pasado a print es un objeto Error
        call_args = mock_print.call_args[0]
        assert isinstance(call_args[0], Error)
        # Verificar que el mensaje del error es el esperado
        assert str(call_args[0]) == "Error de base de datos"
    
def test_get_product_price_success(mock_ordered_products):
    """
    Verifica que cuando la base de datos devuelve un precio para un producto,
    get_product_price retorne dicho valor.
    """
    # Arrange
    mock_ordered_products.fac_db = mock.Mock()
    # Simulamos que se obtiene el precio 9.99 para "Pasta"
    mock_ordered_products.fac_db.read_val.return_value = [(9.99,)]
    
    # Act
    price = mock_ordered_products.get_product_price("Pasta")
    
    # Assert
    assert price == 9.99
    mock_ordered_products.fac_db.read_val.assert_called_once_with(
        "SELECT product_price FROM menu_config WHERE product_name = ?", ("Pasta",)
    )

def test_store_cooked_orders_no_previous(mock_ordered_products):
    """
    Caso 1 (TC1): No existe ningún registro previo en cooked_orders
    Treeview con un ítem: ("Burger", "x2", "Cooked")
    get_product_price("Burger") -> 5.0
    fac_db.read_val(load_query) -> []
    """
    # Arrange
    mock_ordered_products.fac_db = mock.Mock()
    mock_ordered_products.get_product_price = mock.Mock(return_value=5.0)
    
    # Simulamos la ausencia de registros previos
    mock_ordered_products.fac_db.read_val.return_value = []
    
    mock_ordered_products.tr_view.get_children.return_value = ["item1"]
    mock_ordered_products.tr_view.item.return_value = ("Burger", "x2", "Cooked")
    
    # Act
    mock_ordered_products.store_cooked_orders()
    
    # Assert
    # Se espera que order_id sea 1, t_num = 1, or_name = "Burger", or_quantity = 2, or_total = 10.0
    mock_ordered_products.fac_db.insert_spec_config.assert_called_once_with(
        "INSERT INTO cooked_orders VALUES (?, ?, ?,  ?, ?)",
        (1, mock_ordered_products.t_num, "Burger", 2, 10.0)
    )

def test_store_cooked_orders_with_previous(mock_ordered_products):
    """
    Caso 2 (TC2): Sí existe registro previo, último id = 5
    Treeview con un ítem: ("Fries", "x3", "Cooked")
    get_product_price("Fries") -> 3.0
    fac_db.read_val(load_query) -> [(5, '...', '...', ...)]
    """
    # Arrange
    mock_ordered_products.fac_db = mock.Mock()
    mock_ordered_products.get_product_price = mock.Mock(return_value=3.0)

    # Simulamos que ya existe un registro previo con id = 5
    mock_ordered_products.fac_db.read_val.return_value = [(5, 1, "dummy", 1, 1.0)]
    
    mock_ordered_products.tr_view.get_children.return_value = ["item1"]
    mock_ordered_products.tr_view.item.return_value = ("Fries", "x3", "Cooked")
    
    # Act
    mock_ordered_products.store_cooked_orders()
    
    # Assert
    # Se espera que el nuevo id sea 6 y or_total = 3 * 3.0 = 9.0
    mock_ordered_products.fac_db.insert_spec_config.assert_called_once_with(
        "INSERT INTO cooked_orders VALUES (?, ?, ?,  ?, ?)",
        (6, mock_ordered_products.t_num, "Fries", 3, 9.0)
    )

def test_store_cooked_orders_multiple_items(mock_ordered_products):
    """
    Caso 3 (TC3): Múltiples ítems en el Treeview
    Items:
      ("Burger", "x2", "Cooked") -> precio unitario = 5.0
      ("Fries", "x3", "Cooked") -> precio unitario = 2.0
    fac_db.read_val(load_query) -> [] en cada iteración
    """
    # Arrange
    mock_ordered_products.fac_db = mock.Mock()
    # Queremos diferentes respuestas para cada llamada a get_product_price:
    #   - "Burger" => 5.0, "Fries" => 2.0
    def side_effect_price(product_name):
        return 5.0 if product_name == "Burger" else 2.0
    # Crear un mock para get_product_price
    mock_ordered_products.get_product_price = mock.Mock(side_effect=side_effect_price)
    
    # Simulamos que no hay registros previos (retorna [] siempre)
    mock_ordered_products.fac_db.read_val.return_value = []
    
    # Configuramos el Treeview con 2 ítems
    mock_ordered_products.tr_view.get_children.return_value = ["item1", "item2"]
    def side_effect_item(item, _):
        return ("Burger", "x2", "Cooked") if item == "item1" else ("Fries", "x3", "Cooked")
    mock_ordered_products.tr_view.item.side_effect = side_effect_item

    # Para controlar la creación de id, fingimos que store_cooked_orders pregunta la DB cada vez.
    # En este ejemplo, al retornar [] cada vez, siempre interpretará que no hay registros previos.
    # Por lo tanto, ambos ítems obtendrán id=1. (Si tu lógica real incrementa uno a uno, habría que
    # simularlo con side_effect. Mantengamos esta simplificación.)
    
    # Act
    mock_ordered_products.store_cooked_orders()
    
    # Assert
    # Verificamos que se llamara insert_spec_config 2 veces
    assert mock_ordered_products.fac_db.insert_spec_config.call_count == 2
    
    # Revisamos que los parámetros coincidan con los valores esperados
    calls = [
        mock.call(
            "INSERT INTO cooked_orders VALUES (?, ?, ?,  ?, ?)",
            (1, mock_ordered_products.t_num, "Burger", 2, 10.0)
        ),
        mock.call(
            "INSERT INTO cooked_orders VALUES (?, ?, ?,  ?, ?)",
            (1, mock_ordered_products.t_num, "Fries", 3, 6.0)
        )
    ]
    mock_ordered_products.fac_db.insert_spec_config.assert_has_calls(calls, any_order=False)

def test_store_cooked_orders_exception(mock_ordered_products):
    """
    Caso 4 (TC4): Se lanza una excepción al consultar la base de datos
    """
    # Arrange
    mock_ordered_products.fac_db = mock.Mock()
    mock_ordered_products.fac_db.read_val.side_effect = Error("Database error")
    mock_ordered_products.tr_view.get_children.return_value = ["item1"]
    mock_ordered_products.tr_view.item.return_value = ("Burger", "x2", "Cooked")

    # Act & Assert
    with mock.patch("builtins.print") as mock_print:
        mock_ordered_products.store_cooked_orders()
        # Verificar que print fue llamado una vez
        assert mock_print.call_count == 1
        # Verificar que el argumento pasado a print es un objeto Error
        call_args = mock_print.call_args[0]
        assert isinstance(call_args[0], Error)
        # Verificar que el mensaje del error es el esperado
        assert str(call_args[0]) == "Database error"
        # Verificamos que NO se haya llamado a insert_spec_config
        mock_ordered_products.fac_db.insert_spec_config.assert_not_called()

def test_update_order_db_success(mock_ordered_products):
    """
    Caso 1 (TB1): Se llama a update_order_db y se espera que 
    se invoque delete_val con ("DELETE FROM orders WHERE order_status = ?", ["Cooked"])
    sin imprimir ningún error.
    """
    # Arrange
    mock_ordered_products.fac_db = mock.Mock()

    # Act
    mock_ordered_products.update_order_db()

    # Assert
    mock_ordered_products.fac_db.delete_val.assert_called_once_with(
        "DELETE FROM orders WHERE order_status = ?", ["Cooked"]
    )

def test_update_order_db_exception(mock_ordered_products):
    """
    Caso 2 (TB2): Se llama a update_order_db y fac_db.delete_val lanza Error("Database error").
    Se espera que se capture la excepción e imprima 'Database error'.
    """
    # Arrange
    mock_ordered_products.fac_db = mock.Mock()
    mock_ordered_products.fac_db.delete_val.side_effect = Error("Database error")

    with mock.patch("builtins.print") as mock_print:
        # Act
        mock_ordered_products.update_order_db()

        # Assert
        # Verificar que print fue llamado una vez
        assert mock_print.call_count == 1
        # Verificar que el argumento pasado a print es un objeto Error
        call_args = mock_print.call_args[0]
        assert isinstance(call_args[0], Error)
        # Verificar que el mensaje del error es el esperado
        assert str(call_args[0]) == "Database error"
        # Verificar que se llamó a delete_val con los parámetros correctos
        mock_ordered_products.fac_db.delete_val.assert_called_once_with(
            "DELETE FROM orders WHERE order_status = ?", ["Cooked"]
        )
    
def test_fulfil_order_notebook_not_empty(mock_ordered_products):
    """
    Caso 1 (TB1): fulfil_order() se llama cuando root_frame.tabs() 
    aún tiene elementos, por ejemplo ["tab1"].
    Se espera:
     - self.store_cooked_orders()
     - self.update_order_db()
     - self.destroy()
     - self.root_frame.forget(self.tb)
     - NO se llama a self.f()
    """
    # Arrange
    mock_ordered_products.store_cooked_orders = mock.Mock()
    mock_ordered_products.update_order_db = mock.Mock()
    mock_ordered_products.destroy = mock.Mock()
    
    # Agregar el atributo tb que falta
    mock_ordered_products.tb = mock.Mock()
    
    # Simulamos que hay una pestaña abierta
    mock_ordered_products.root_frame.tabs.return_value = ["tab1"]

    # Act
    mock_ordered_products.fulfil_order()

    # Assert
    mock_ordered_products.store_cooked_orders.assert_called_once()
    mock_ordered_products.update_order_db.assert_called_once()
    mock_ordered_products.destroy.assert_called_once()
    mock_ordered_products.root_frame.forget.assert_called_once_with(mock_ordered_products.tb)
    mock_ordered_products.f.assert_not_called()

def test_fulfil_order_notebook_empty(mock_ordered_products):
    """
    Caso 2 (TB2): fulfil_order() se llama cuando root_frame.tabs() 
    devuelve una lista vacía (ninguna pestaña).
    Se espera:
     - self.store_cooked_orders()
     - self.update_order_db()
     - self.destroy()
     - self.root_frame.forget(self.tb)
     - Sí se llama a self.f()
    """
    # Arrange
    mock_ordered_products.store_cooked_orders = mock.Mock()
    mock_ordered_products.update_order_db = mock.Mock()
    mock_ordered_products.destroy = mock.Mock()
    
    # Agregar el atributo tb que falta
    mock_ordered_products.tb = mock.Mock()
    
    # Simulamos que no quedan pestañas
    mock_ordered_products.root_frame.tabs.return_value = []

    # Act
    mock_ordered_products.fulfil_order()

    # Assert
    mock_ordered_products.store_cooked_orders.assert_called_once()
    mock_ordered_products.update_order_db.assert_called_once()
    mock_ordered_products.destroy.assert_called_once()
    mock_ordered_products.root_frame.forget.assert_called_once_with(mock_ordered_products.tb)
    mock_ordered_products.f.assert_called_once()

def test_selected_item(mock_ordered_products):
    """
    Verifica que, al llamar a selected_item(event),
    se habilite cooked_btn (state=tk.ACTIVE) y se invoque check_for_cooked().
    """
    # Configurar el mock para que get_children devuelva una lista vacía
    mock_ordered_products.tr_view.get_children.return_value = []
    
    # Crear un mock para check_for_cooked para evitar que se ejecute el método real
    mock_ordered_products.check_for_cooked = mock.Mock()
    
    event = mock.Mock()
    # Llamamos al método
    mock_ordered_products.selected_item(event)
    
    # Verificamos que se llame cooked_btn.config con state=tk.ACTIVE
    mock_ordered_products.cooked_btn.config.assert_called_with(state=tk.ACTIVE)
    # Verificamos que se invoque check_for_cooked
    mock_ordered_products.check_for_cooked.assert_called_once()

def test_change_state(mock_ordered_products):
    """
    Caso (TB1): Se selecciona un ítem en el Treeview con valores ("Burger", "x1", "Ordered")
    Al llamar a change_state(), el ítem debe actualizarse a ("Burger", "x1", "Cooked")
    y se deben invocar update_order_status y check_for_cooked.
    """
    # Arrange
    mock_ordered_products.tr_view.focus.return_value = "item1"
    mock_ordered_products.tr_view.item.return_value = ("Burger", "x1", "Ordered")

    # Parches para verificar que se llaman después
    mock_ordered_products.update_order_status = mock.Mock()
    mock_ordered_products.check_for_cooked = mock.Mock()

    # Act
    mock_ordered_products.change_state()

    # Assert
    # Verificar que se llamó a item dos veces
    assert mock_ordered_products.tr_view.item.call_count == 2
    
    # Verificar la primera llamada (para obtener los valores)
    mock_ordered_products.tr_view.item.assert_any_call("item1", "values")
    
    # Verificar la segunda llamada (para actualizar los valores)
    mock_ordered_products.tr_view.item.assert_any_call(
        "item1", text="", values=("Burger", "x1", "Cooked")
    )
    
    # Verificar que se llamaron los otros métodos
    mock_ordered_products.update_order_status.assert_called_once()
    mock_ordered_products.check_for_cooked.assert_called_once()

import pytest
from unittest import mock
from BASE.Components.printorders import PrintOrders
import tkinter as tk
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

def test_load_orders_loop(mock_print_orders):
    """Prueba que load_orders ejecuta correctamente el bucle cuando se retornan múltiples órdenes."""
    # Configurar el valor del número de mesa
    mock_print_orders.tb_name_entry.get.return_value = "1"
    
    # Simular que la base de datos retorna tres órdenes
    orders_result = [
        (1, "Product1", 2, 20.0),
        (2, "Product2", 1, 15.0),
        (3, "Product3", 3, 30.0)
    ]
    mock_print_orders.fac_db.read_val.return_value = orders_result

    # Asegurarse de que insert esté limpio (resetear llamadas previas)
    mock_print_orders.tr_view.insert.reset_mock()

    # Ejecutar load_orders (que es la función a probar)
    mock_print_orders.load_orders()

    # Verificar que se llamó a fac_db.read_val una vez
    mock_print_orders.fac_db.read_val.assert_called_once()
    
    # Verificar que por cada orden se llamó a tr_view.insert, es decir, 3 veces
    assert mock_print_orders.tr_view.insert.call_count == 3

    # Verificar que cada llamada a tr_view.insert fue con los valores esperados
    expected_calls = [
        mock.call("", tk.END, values=(1, "Product1", 2, f"{20.0:.2f}")),
        mock.call("", tk.END, values=(2, "Product2", 1, f"{15.0:.2f}")),
        mock.call("", tk.END, values=(3, "Product3", 3, f"{30.0:.2f}"))
    ]
    mock_print_orders.tr_view.insert.assert_has_calls(expected_calls, any_order=False)

    # Verificar que se configuró el botón de impresión a 'active'
    mock_print_orders.print_receipt_btn.config.assert_called_once_with(state='active')



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

def test_print_receipt_valid_orders(mock_print_orders):
    """Prueba que print_receipt genera correctamente el recibo cuando hay órdenes válidas."""
    # Configurar el valor de t_num
    mock_print_orders.t_num = "1"

    # Simular que el Treeview tiene dos elementos
    mock_print_orders.tr_view.get_children.return_value = ["child1", "child2"]

    # Definir el comportamiento de tr_view.item para cada hijo
    def item_side_effect(child):
        if child == "child1":
            # Valores: id, product name, quantity, price (en formato de string para el precio)
            return {"values": [1, "Product1", 2, "20.00"]}
        elif child == "child2":
            return {"values": [2, "Product2", 1, "15.00"]}
    mock_print_orders.tr_view.item.side_effect = item_side_effect

    # Preparar un contenido de plantilla HTML de ejemplo
    sample_template = '<html><body><div>Fac_name</div><div>t_num</div></body></html>'
    m_open = mock.mock_open(read_data=sample_template)

    with mock.patch("builtins.open", m_open):
        with mock.patch("webbrowser.open_new_tab") as mock_open_tab:
            with mock.patch.object(mock_print_orders, "clear_all") as mock_clear_all:
                # Ejecutar print_receipt
                mock_print_orders.print_receipt()
                
                # Verificar que se abrió el archivo para escritura con el nombre esperado
                m_open.assert_any_call("order_1.html", "w+", encoding='utf-8')
                # Verificar que se llamó a webbrowser.open_new_tab con el nombre del archivo
                mock_open_tab.assert_called_once_with("order_1.html")
                # Verificar que clear_all fue llamado al finalizar
                mock_clear_all.assert_called_once()

def test_print_receipt_no_orders(mock_print_orders):
    """Prueba que print_receipt genera el recibo correctamente cuando no hay órdenes en el Treeview."""
    # Configurar el valor de t_num
    mock_print_orders.t_num = "1"

    # Simular que el Treeview no contiene elementos
    mock_print_orders.tr_view.get_children.return_value = []
    
    # Preparar un contenido de plantilla HTML de ejemplo
    sample_template = '<html><body><div>Fac_name</div><div>t_num</div></body></html>'
    m_open = mock.mock_open(read_data=sample_template)

    with mock.patch("builtins.open", m_open):
        with mock.patch("webbrowser.open_new_tab") as mock_open_tab:
            with mock.patch.object(mock_print_orders, "clear_all") as mock_clear_all:
                # Ejecutar print_receipt
                mock_print_orders.print_receipt()
                
                # Verificar que se abrió el archivo para escritura con el nombre esperado
                m_open.assert_any_call("order_1.html", "w+", encoding='utf-8')
                # Verificar que se llamó a webbrowser.open_new_tab con "order_1.html"
                mock_open_tab.assert_called_once_with("order_1.html")
                # Verificar que clear_all fue llamado al finalizar
                mock_clear_all.assert_called_once()

def test_clear_all_with_children(mock_print_orders):
    """Prueba que clear_all limpia correctamente el Treeview cuando tiene elementos."""
    # Configurar mocks
    mock_print_orders.tb_name_entry.delete = mock.Mock()
    # Simular que el Treeview tiene elementos
    mock_print_orders.tr_view.get_children.return_value = ["child1", "child2"]
    mock_print_orders.tr_view.delete = mock.Mock()
    # Ejecutar clear_all
    mock_print_orders.clear_all()
    
    # Verificar que se eliminó el contenido del entry
    mock_print_orders.tb_name_entry.delete.assert_called_once_with(0, tk.END)
    # Verificar que se llamo a delete para cada hijo
    expected_calls = [mock.call("child1"), mock.call("child2")]
    mock_print_orders.tr_view.delete.assert_has_calls(expected_calls, any_order=False)
    # Verificar que se desactiva el botón
    mock_print_orders.print_receipt_btn.config.assert_called_once_with(state=tk.DISABLED)

def test_clear_all_without_children(mock_print_orders):
    """Prueba que clear_all limpia correctamente el Treeview cuando no tiene elementos."""
    # Configurar mocks
    mock_print_orders.tb_name_entry.delete = mock.Mock()
    # Simular que el Treeview no tiene elementos
    mock_print_orders.tr_view.get_children.return_value = []
    mock_print_orders.tr_view.delete = mock.Mock()
    # Ejecutar clear_all
    mock_print_orders.clear_all()
    
    # Verificar que se eliminó el contenido del entry
    mock_print_orders.tb_name_entry.delete.assert_called_once_with(0, tk.END)
    # Verificar que tr_view.delete no se llamó ya que no hay elementos
    mock_print_orders.tr_view.delete.assert_not_called()
    # Verificar que se desactiva el botón
    mock_print_orders.print_receipt_btn.config.assert_called_once_with(state=tk.DISABLED)

def test_html_order(mock_print_orders):
    """Prueba que html_order genera los fragmentos HTML correctos para un producto."""
    # Parámetros de ejemplo
    top_pad = 1
    name = "Product1"
    quantity = 2
    price = "20.00"
    result = mock_print_orders.html_order(top_pad, name, quantity, price)

    # Extraer las tres instancias de BeautifulSoup
    soup_name, soup_quantity, soup_price = result

    # Calcular el valor esperado de 'top' (150 + top_pad*20)
    expected_top = 150 + (top_pad * 20)  # 150 + 20 = 170

    # Buscar el tag <span> en cada fragmento (por si se envolvió en <html><body>...)
    tag_name = soup_name.find('span')
    tag_quantity = soup_quantity.find('span')
    tag_price = soup_price.find('span')

    # Verificar que se incluya el estilo con top esperado
    assert f"top:{expected_top}pt;" in tag_name.get("style", "")
    assert f"top:{expected_top}pt;" in tag_quantity.get("style", "")
    assert f"top:{expected_top}pt;" in tag_price.get("style", "")

    # Verificar que los textos sean correctos (usando get_text(strip=True) para eliminar espacios y saltos de línea)
    assert tag_name.get_text(strip=True) == name
    assert tag_quantity.get_text(strip=True) == f"x{quantity}"
    assert tag_price.get_text(strip=True) == price

def test_destroy_calls_super_destroy(mock_print_orders):
    """Prueba que destroy llama al método destroy de la clase base."""
    # Se puede hacer un patch en el objeto super y comprobar que se llama
    with mock.patch.object(type(mock_print_orders), 'destroy', autospec=True) as mock_super_destroy:
        mock_print_orders.destroy()
        mock_super_destroy.assert_called_once_with(mock_print_orders)


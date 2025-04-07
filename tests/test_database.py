import pytest
from unittest import mock
from BASE.Components.Database import Database
import os
from sqlite3 import Error


@pytest.fixture
def mock_db():
    """Fixture que crea una instancia de Database con conexión y cursor mockeados"""
    # Crear una ruta de base de datos de prueba
    test_db_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test.db')
    os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
    
    with mock.patch('sqlite3.connect') as mock_connect:
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        db = Database(test_db_path)  # Proporcionar la ruta de la base de datos
        db.conn = mock_conn
        db.cursor = mock_cursor
        return db

def test_read_val_success(mock_db):
    """Prueba que read_val retorna el valor correcto cuando la lectura es exitosa"""
    # Configurar el mock para simular una lectura exitosa
    mock_db.cursor.fetchall.return_value = [("test_value",)]
    
    # Crear una consulta SQL de prueba
    test_query = "SELECT test_column FROM test_table WHERE test_where_col = ?"
    test_value = "test_where_val"
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    
    result = mock_db.read_val(test_query, test_value)
    
    assert result == [("test_value",)]
    mock_db.cursor.execute.assert_called_once_with(test_query, test_value)

def test_read_val_without_where(mock_db):
    """Prueba que read_val funciona correctamente sin cláusula WHERE"""
    mock_db.cursor.fetchall.return_value = [("value1",), ("value2",)]
    test_query = "SELECT * FROM test_table"
    
    mock_db.cursor.execute.reset_mock()
    
    result = mock_db.read_val(test_query)
    
    assert result == [("value1",), ("value2",)]
    mock_db.cursor.execute.assert_called_once_with(test_query)

def test_read_val_error(mock_db):
    """Prueba que read_val maneja correctamente los errores"""
    mock_db.cursor.execute.side_effect = Error("Test error")
    
    result = mock_db.read_val("SELECT * FROM test_table")
    
    assert result is None

def test_create_table_success(mock_db):
    """Prueba que create_table crea una tabla correctamente"""
    test_query = "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    mock_db.conn.commit.reset_mock()
    
    mock_db.create_table(test_query)
    
    # Verificar que se llamó a execute y commit
    mock_db.cursor.execute.assert_called_once_with(test_query)
    mock_db.conn.commit.assert_called_once()

def test_create_table_error(mock_db):
    """Prueba que create_table maneja correctamente los errores"""
    mock_db.cursor.execute.side_effect = Error("Test error")
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    mock_db.conn.commit.reset_mock()
    
    mock_db.create_table("CREATE TABLE test_table (id INTEGER PRIMARY KEY)")
    
    # Verificar que no se llamó a commit cuando hay error
    mock_db.conn.commit.assert_not_called()

def test_insert_spec_config_success(mock_db):
    """Prueba que insert_spec_config inserta datos correctamente"""
    test_query = "INSERT INTO test_table (id, name) VALUES (?, ?)"
    test_values = (1, "test_name")
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    mock_db.conn.commit.reset_mock()
    
    mock_db.insert_spec_config(test_query, test_values)
    
    # Verificar que se llamó a execute y commit
    mock_db.cursor.execute.assert_called_once_with(test_query, test_values)
    mock_db.conn.commit.assert_called_once()

def test_insert_spec_config_error(mock_db):
    """Prueba que insert_spec_config maneja correctamente los errores"""
    mock_db.cursor.execute.side_effect = Error("Test error")
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    mock_db.conn.commit.reset_mock()
    
    mock_db.insert_spec_config("INSERT INTO test_table VALUES (?)", (1,))
    
    # Verificar que no se llamó a commit cuando hay error
    mock_db.conn.commit.assert_not_called()

def test_update_success(mock_db):
    """Prueba que update actualiza datos correctamente"""
    test_query = "UPDATE test_table SET name = ? WHERE id = ?"
    test_values = ("new_name", 1)
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    mock_db.conn.commit.reset_mock()
    
    mock_db.update(test_query, test_values)
    
    # Verificar que se llamó a execute y commit
    mock_db.cursor.execute.assert_called_once_with(test_query, test_values)
    mock_db.conn.commit.assert_called_once()

def test_update_error(mock_db):
    """Prueba que update maneja correctamente los errores"""
    mock_db.cursor.execute.side_effect = Error("Test error")
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    mock_db.conn.commit.reset_mock()
    
    mock_db.update("UPDATE test_table SET name = ?", ("test_name",))
    
    # Verificar que no se llamó a commit cuando hay error
    mock_db.conn.commit.assert_not_called()

def test_delete_val_success(mock_db):
    """Prueba que delete_val elimina datos correctamente"""
    test_query = "DELETE FROM test_table WHERE id = ?"
    test_id = 1
    
    # Limpiar el historial de llamadas antes de nuestra prueba
    mock_db.cursor.execute.reset_mock()
    mock_db.conn.commit.reset_mock()
    
    mock_db.delete_val(test_query, test_id)
    
    # Verificar que se llamó a execute y commit
    mock_db.cursor.execute.assert_called_once_with(test_query, test_id)
    mock_db.conn.commit.assert_called_once()


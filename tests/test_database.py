import pytest
from unittest import mock
from BASE.Components.Database import Database
import os


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
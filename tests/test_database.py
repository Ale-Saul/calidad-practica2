import pytest
from unittest import mock
from BASE.Components.Database import Database

@pytest.fixture
def mock_db():
    """Fixture que crea una instancia de Database con conexión y cursor mockeados"""
    with mock.patch('sqlite3.connect') as mock_connect:
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        db = Database()
        db.conn = mock_conn
        db.cursor = mock_cursor
        return db

def test_read_val_success(mock_db):
    """Prueba que read_val retorna el valor correcto cuando la lectura es exitosa"""
    # Configurar el mock para simular una lectura exitosa
    mock_db.cursor.fetchone.return_value = ("test_value",)
    
    result = mock_db.read_val("test_table", "test_column", "test_where_col", "test_where_val")
    
    assert result == "test_value"
    mock_db.cursor.execute.assert_called_once() 
import pytest
from unittest.mock import Mock, patch
from BASE.Components.configwindow import ConfigWindow  

@pytest.fixture
def mock_parent():
    return Mock()

@pytest.fixture
def config_window(mock_parent):
    return ConfigWindow(mock_parent, lambda: None)


#Test 1:Verificar que la validación lanza error si se ingresan más de 50 mesas
def test_callback_table_valid(config_window):
    assert config_window.callback_table("30") is True
    assert config_window.callback_table("50") is True
    assert config_window.callback_table("") is True

def test_callback_table_invalid(config_window):
    with patch("tkinter.messagebox.showerror") as mock_msg:
        assert config_window.callback_table("60") is False
        mock_msg.assert_called_once()


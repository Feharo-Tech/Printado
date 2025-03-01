import pytest
from printado.core.utils import delete_temp_screenshot
import os

def test_delete_temp_screenshot():
    """Testa a remoção do arquivo de captura temporária."""
    temp_file = "temp_screenshot.png"
    open(temp_file, "w").close()  # Cria um arquivo temporário

    assert os.path.exists(temp_file)  # Confirma que o arquivo existe
    delete_temp_screenshot()
    assert not os.path.exists(temp_file)  # Confirma que foi removido

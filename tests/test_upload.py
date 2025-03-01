import pytest
from printado.modules.upload import UploadThread
from PyQt5.QtCore import QThread

@pytest.fixture
def upload_thread():
    return UploadThread("test_image.png")

def test_upload_thread_creation(upload_thread):
    """Verifica se a thread de upload é criada corretamente."""
    assert isinstance(upload_thread, QThread)

def test_upload_thread_signal(upload_thread, qtbot):
    """Testa se a thread de upload emite um sinal ao concluir."""
    def mock_upload_finished(link):
        assert "http" in link or "Erro" in link

    upload_thread.upload_finished.connect(mock_upload_finished)
    qtbot.waitSignal(upload_thread.upload_finished, timeout=5000)

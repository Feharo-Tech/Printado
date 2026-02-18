from PyQt5.QtCore import QThread

from printado.modules.upload import UploadThread


class _FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


def test_upload_thread_creation():
    thread = UploadThread(image_bytes=b"png-bytes", filename="test.png")
    assert isinstance(thread, QThread)


def test_upload_thread_emits_link(monkeypatch):
    def fake_post(url, files=None, headers=None, timeout=None):
        return _FakeResponse(200, payload={"link": "https://example.com/x"})

    monkeypatch.setattr("printado.modules.upload.requests.post", fake_post)

    emitted = {"value": None}
    thread = UploadThread(image_bytes=b"png-bytes", filename="test.png")
    thread.upload_finished.connect(lambda value: emitted.__setitem__("value", value))
    thread.run()

    assert emitted["value"] == "https://example.com/x"

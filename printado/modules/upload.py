import io
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from printado.config import Config

class UploadThread(QThread):
    upload_finished = pyqtSignal(str)

    def __init__(self, filepath=None, image_bytes=None, filename="screenshot.png"):
        super().__init__()
        self.filepath = filepath
        self.image_bytes = image_bytes
        self.filename = filename

    def run(self):
        try:
            headers = {"X-API-KEY": Config.API_KEY}

            if self.image_bytes is not None:
                file_obj = io.BytesIO(self.image_bytes)
                files = {"image": (self.filename, file_obj, "image/png")}
            elif self.filepath:
                file_obj = open(self.filepath, "rb")
                files = {"image": file_obj}
            else:
                raise ValueError("Nenhuma imagem fornecida para upload.")

            try:
                response = requests.post(Config.UPLOAD_URL, files=files, headers=headers, timeout=10)
            finally:
                try:
                    file_obj.close()
                except Exception:
                    pass

            status_code = response.status_code
            response_text = response.text

            if status_code == 200:
                try:
                    response_json = response.json()
                    link = response_json.get("link", "")

                    if link:
                        self.upload_finished.emit(link)
                    else:
                        raise ValueError("Resposta do servidor não contém um link válido.")

                except Exception:
                    self.upload_finished.emit("Erro ao processar a resposta do servidor.")

            else:
                print(f"❌ Erro HTTP {status_code}: {response_text}")
                self.upload_finished.emit(f"Erro {status_code}: {response_text}")

        except requests.exceptions.Timeout:
            self.upload_finished.emit("Erro: O servidor demorou muito para responder.")

        except requests.exceptions.ConnectionError:
            self.upload_finished.emit("Erro de conexão: O servidor está indisponível.")

        except requests.exceptions.RequestException as e:
            self.upload_finished.emit(f"Erro de rede: {str(e)}")

        except Exception as e:
            self.upload_finished.emit(f"Erro desconhecido: {str(e)}")

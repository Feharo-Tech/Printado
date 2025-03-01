import os
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from printado.config import Config

class UploadThread(QThread):
    upload_finished = pyqtSignal(str)

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):

        try:
            with open(self.filepath, "rb") as file:
                headers = {"X-API-KEY": Config.API_KEY}
                response = requests.post(Config.UPLOAD_URL, files={"image": file}, headers=headers, timeout=10)

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

                except Exception as e:
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

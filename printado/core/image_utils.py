import io

from PyQt5.QtGui import QImage, QPixmap


def pil_image_to_qpixmap(pil_image) -> QPixmap:
    """Convert a PIL Image to a QPixmap without disk IO."""
    image = pil_image.convert("RGBA")
    data = image.tobytes("raw", "RGBA")
    qimage = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimage)


def pil_image_to_png_bytes(pil_image) -> bytes:
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()

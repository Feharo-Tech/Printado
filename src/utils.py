from PIL import ImageFont

def load_font():
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except IOError:
        return ImageFont.load_default()
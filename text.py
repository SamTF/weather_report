### ENUM OF AVAILABLE FONTS
from enum import Enum
from PIL import ImageFont

class Font(Enum):
    BOLD            = ImageFont.truetype('/fonts/MyriadPro-Bold.otf',       130)
    CONDENSED       = ImageFont.truetype("/fonts/MyriadPro-Cond.otf",       64)
    BOLD_CONDENSED  = ImageFont.truetype("/fonts/MyriadPro-BoldCond.otf",   72)
    

### TEXT FORMATTING CLASS ###
class Text:
    def __init__(self, text, position, font, colour=(0,0,0), anchor='lm') -> None:
        self.text       = text
        self.position   = position
        self.font       = font
        self.colour     = colour
        self.anchor     = anchor    # https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
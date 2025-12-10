from PIL import Image
import time
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
FRAME_WIDTH = 64         # width of animation frame
FRAME_HEIGHT = 64        # height of animation frame
FRAME_DELAY = 0.05

# The blue region starts BELOW the yellow strip.
# For most 1.3" 128x64 OLEDs:
YELLOW_HEIGHT = 16       # top 16px are yellow
BLUE_START_Y = YELLOW_HEIGHT
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

# Ensure animation stays inside BLUE area
MAX_Y_OFFSET = DISPLAY_HEIGHT - BLUE_START_Y - FRAME_HEIGHT
SAFE_Y_OFFSET = max(0, MAX_Y_OFFSET)

# -------------------------------------------------------
# Hardware initialize
# -------------------------------------------------------
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

# -------------------------------------------------------
# Helper: scale frames to always fit
# -------------------------------------------------------
def scale_frame_if_needed(img):
    if FRAME_HEIGHT > (DISPLAY_HEIGHT - YELLOW_HEIGHT):
        scale_factor = (DISPLAY_HEIGHT - YELLOW_HEIGHT) / FRAME_HEIGHT
        new_w = int(FRAME_WIDTH * scale_factor)
        new_h = int(FRAME_HEIGHT * scale_factor)
        return img.resize((new_w, new_h), Image.NEAREST)
    return img

# -------------------------------------------------------
# MAIN LOOP: draw every frame inside blue zone only
# -------------------------------------------------------
while True:
    for frame in frames:
        # Convert raw bytes → PIL image
        img = Image.frombytes("1", (FRAME_WIDTH, FRAME_HEIGHT), frame)

        # Auto-scale if needed
        img = scale_frame_if_needed(img)
        w, h = img.size

        # Place image ONLY inside blue region
        x = (DISPLAY_WIDTH - w) // 2      # centered horizontally
        y = BLUE_START_Y                  # locked to blue area

        # Prepare output
        full_img = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        full_img.paste(img, (x, y))

        device.display(full_img)
        time.sleep(FRAME_DELAY)

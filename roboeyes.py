# roboeyes_full.py
"""
Full Python port (1:1) of FluxGarage RoboEyes for Raspberry Pi + OLED
Implements nearly all features from the Arduino version:
- moods: DEFAULT, TIRED, ANGRY, HAPPY
- autoblinker, idle, confused, laugh
- horizontal / vertical flicker
- sweat drops (3)
- cyclops / curiosity
- rounded eyes, triangular eyelids, happy bottom eyelid
- smooth tweening ("Next" values)
Use with luma.oled (ssd1306 or ssd1327) + Pillow.
"""

import time
import random
from math import floor
from PIL import Image, ImageDraw

# If using luma:
try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306, ssd1327
except Exception:
    # luma not installed — you can still import this module and use draw_frame_to_image()
    ssd1306 = None
    ssd1327 = None
    i2c = None

# Constants (mood/type flags)
DEFAULT = 0
TIRED = 1
ANGRY = 2
HAPPY = 3

ON = True
OFF = False

BLUE_START_Y = 16
BLUE_HEIGHT = 48
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

# position definitions (not strictly necessary but included for parity)
N = 1; NE = 2; E = 3; SE = 4; S = 5; SW = 6; W = 7; NW = 8

def millis():
    """Arduino-like millis() in milliseconds."""
    return int(time.monotonic() * 1000)


class RoboEyes:
    def __init__(self, device=None, width=128, height=64, frame_rate=50, monochrome=True):
        """
        device: luma device or None. If None, you can still call draw_frame_to_image() to get PIL Image.
        width/height: screen pixel dimensions
        frame_rate: target FPS
        monochrome: True uses mode '1' (0/1), False uses 'L' (0/255). Defaults to True.
        """
        self.device = device
        self.screenWidth = width
        self.screenHeight = height
        self.monochrome = monochrome

        # Colors (0/1 or 0/255)
        self.BGCOLOR = 0
        self.MAINCOLOR = 1 if monochrome else 255

        # Frame timing
        self.frameInterval = 1000 // frame_rate  # ms
        self.fpsTimer = millis()

        # Mood flags
        self.tired = False
        self.angry = False
        self.happy = False
        self.curious = False
        self.cyclops = False
        self.eyeL_open = False
        self.eyeR_open = False

        # Eye defaults and current values
        self.eyeLwidthDefault = 36
        self.eyeLheightDefault = 36
        self.eyeLwidthCurrent = self.eyeLwidthDefault
        self.eyeLheightCurrent = 1  # start closed
        self.eyeLwidthNext = self.eyeLwidthDefault
        self.eyeLheightNext = self.eyeLheightDefault
        self.eyeLheightOffset = 0
        self.eyeLborderRadiusDefault = 8
        self.eyeLborderRadiusCurrent = self.eyeLborderRadiusDefault
        self.eyeLborderRadiusNext = self.eyeLborderRadiusDefault

        self.eyeRwidthDefault = self.eyeLwidthDefault
        self.eyeRheightDefault = self.eyeLheightDefault
        self.eyeRwidthCurrent = self.eyeRwidthDefault
        self.eyeRheightCurrent = 1
        self.eyeRwidthNext = self.eyeRwidthDefault
        self.eyeRheightNext = self.eyeRheightDefault
        self.eyeRheightOffset = 0
        self.eyeRborderRadiusDefault = 8
        self.eyeRborderRadiusCurrent = self.eyeRborderRadiusDefault
        self.eyeRborderRadiusNext = self.eyeRborderRadiusDefault

        # space between eyes default
        self.spaceBetweenDefault = 10
        self.spaceBetweenCurrent = self.spaceBetweenDefault
        self.spaceBetweenNext = self.spaceBetweenDefault

        # default eye positions (centered)
        self.eyeLxDefault = (self.screenWidth - (self.eyeLwidthDefault + self.spaceBetweenDefault + self.eyeRwidthDefault)) // 2
        self.eyeLyDefault = (self.screenHeight - self.eyeLheightDefault) // 2
        self.eyeLx = self.eyeLxDefault
        self.eyeLy = self.eyeLyDefault
        self.eyeLxNext = self.eyeLx
        self.eyeLyNext = self.eyeLy

        self.eyeRxDefault = self.eyeLx + self.eyeLwidthCurrent + self.spaceBetweenDefault
        self.eyeRyDefault = self.eyeLy
        self.eyeRx = self.eyeRxDefault
        self.eyeRy = self.eyeRyDefault
        self.eyeRxNext = self.eyeRx
        self.eyeRyNext = self.eyeRy

        # eyelids (top)
        self.eyelidsHeightMax = self.eyeLheightDefault // 2
        self.eyelidsTiredHeight = 0
        self.eyelidsTiredHeightNext = 0
        self.eyelidsAngryHeight = 0
        self.eyelidsAngryHeightNext = 0
        # bottom happy eyelid offset
        self.eyelidsHappyBottomOffsetMax = (self.eyeLheightDefault // 2) + 3
        self.eyelidsHappyBottomOffset = 0
        self.eyelidsHappyBottomOffsetNext = 0

        # Macro animations
        self.hFlicker = False
        self.hFlickerAlternate = False
        self.hFlickerAmplitude = 2

        self.vFlicker = False
        self.vFlickerAlternate = False
        self.vFlickerAmplitude = 10

        self.autoblinker = False
        self.blinkInterval = 1
        self.blinkIntervalVariation = 4
        self.blinktimer = millis()

        self.idle = False
        self.idleInterval = 1
        self.idleIntervalVariation = 3
        self.idleAnimationTimer = millis()

        self.confused = False
        self.confusedAnimationTimer = 0
        self.confusedAnimationDuration = 500
        self.confusedToggle = True

        self.laugh = False
        self.laughAnimationTimer = 0
        self.laughAnimationDuration = 500
        self.laughToggle = True

        # Sweat
        self.sweat = False
        self.sweatBorderradius = 3
        # sweat drop 1
        self.sweat1XPosInitial = 2
        self.sweat1XPos = self.sweat1XPosInitial
        self.sweat1YPos = 2.0
        self.sweat1YPosMax = 12
        self.sweat1Height = 2.0
        self.sweat1Width = 1.0
        # drop 2
        self.sweat2XPosInitial = 2
        self.sweat2XPos = self.sweat2XPosInitial
        self.sweat2YPos = 2.0
        self.sweat2YPosMax = 12
        self.sweat2Height = 2.0
        self.sweat2Width = 1.0
        # drop 3
        self.sweat3XPosInitial = 2
        self.sweat3XPos = self.sweat3XPosInitial
        self.sweat3YPos = 2.0
        self.sweat3YPosMax = 12
        self.sweat3Height = 2.0
        self.sweat3Width = 1.0

        # make sure everything else that relies on size is initialised
        self.eyeLheightCurrent = 1
        self.eyeRheightCurrent = 1
        self.eyeLwidthCurrent = self.eyeLwidthDefault
        self.eyeRwidthCurrent = self.eyeRwidthDefault

    # ---------------------------
    # UTIL / SETTERS
    # ---------------------------
    def setFramerate(self, fps):
        self.frameInterval = int(1000 / fps)

    def setDisplayColors(self, background, main):
        self.BGCOLOR = background
        self.MAINCOLOR = main

    def setWidth(self, leftEye, rightEye):
        self.eyeLwidthNext = leftEye
        self.eyeRwidthNext = rightEye
        self.eyeLwidthDefault = leftEye
        self.eyeRwidthDefault = rightEye

    def setHeight(self, leftEye, rightEye):
        self.eyeLheightNext = leftEye
        self.eyeRheightNext = rightEye
        self.eyeLheightDefault = leftEye
        self.eyeRheightDefault = rightEye

    def setBorderradius(self, leftEye, rightEye):
        self.eyeLborderRadiusNext = leftEye
        self.eyeRborderRadiusNext = rightEye
        self.eyeLborderRadiusDefault = leftEye
        self.eyeRborderRadiusDefault = rightEye

    def setSpacebetween(self, space):
        self.spaceBetweenNext = space
        self.spaceBetweenDefault = space

    def setMood(self, mood):
        if mood == TIRED:
            self.tired = True; self.angry = False; self.happy = False
        elif mood == ANGRY:
            self.tired = False; self.angry = True; self.happy = False
        elif mood == HAPPY:
            self.tired = False; self.angry = False; self.happy = True
        else:
            self.tired = False; self.angry = False; self.happy = False

    def setPosition(self, position):
        if position == N:
            self.eyeLxNext = self.getScreenConstraint_X() // 2
            self.eyeLyNext = 0
        elif position == NE:
            self.eyeLxNext = self.getScreenConstraint_X()
            self.eyeLyNext = 0
        elif position == E:
            self.eyeLxNext = self.getScreenConstraint_X()
            self.eyeLyNext = self.getScreenConstraint_Y() // 2
        elif position == SE:
            self.eyeLxNext = self.getScreenConstraint_X()
            self.eyeLyNext = self.getScreenConstraint_Y()
        elif position == S:
            self.eyeLxNext = self.getScreenConstraint_X() // 2
            self.eyeLyNext = self.getScreenConstraint_Y()
        elif position == SW:
            self.eyeLxNext = 0
            self.eyeLyNext = self.getScreenConstraint_Y()
        elif position == W:
            self.eyeLxNext = 0
            self.eyeLyNext = self.getScreenConstraint_Y() // 2
        elif position == NW:
            self.eyeLxNext = 0
            self.eyeLyNext = 0
        else:
            self.eyeLxNext = self.getScreenConstraint_X() // 2
            self.eyeLyNext = self.getScreenConstraint_Y() // 2

    def setAutoblinker(self, active, interval=None, variation=None):
        self.autoblinker = bool(active)
        if interval is not None:
            self.blinkInterval = interval
        if variation is not None:
            self.blinkIntervalVariation = variation

    def setIdleMode(self, active, interval=None, variation=None):
        self.idle = bool(active)
        if interval is not None:
            self.idleInterval = interval
        if variation is not None:
            self.idleIntervalVariation = variation

    def setCuriosity(self, curiousBit):
        self.curious = bool(curiousBit)

    def setCyclops(self, cyclopsBit):
        self.cyclops = bool(cyclopsBit)

    def setHFlicker(self, flickerBit, amplitude=None):
        self.hFlicker = bool(flickerBit)
        if amplitude is not None:
            self.hFlickerAmplitude = amplitude

    def setVFlicker(self, flickerBit, amplitude=None):
        self.vFlicker = bool(flickerBit)
        if amplitude is not None:
            self.vFlickerAmplitude = amplitude

    def setSweat(self, sweatBit):
        self.sweat = bool(sweatBit)

    def getScreenConstraint_X(self):
        return self.screenWidth - self.eyeLwidthCurrent - self.spaceBetweenCurrent - self.eyeRwidthCurrent

    def getScreenConstraint_Y(self):
        return self.screenHeight - self.eyeLheightDefault

    # ---------------------------
    # Blink / open / close
    # ---------------------------
    def close(self, left=True, right=True):
        if left:
            self.eyeLheightNext = 1
            self.eyeL_open = False
        if right:
            self.eyeRheightNext = 1
            self.eyeR_open = False

    def open(self, left=True, right=True):
        if left:
            self.eyeL_open = True
        if right:
            self.eyeR_open = True

    def blink_once(self):
        self.close(True, True)
        self.open(True, True)

    # Animations triggers
    def anim_confused(self):
        self.confused = True

    def anim_laugh(self):
        self.laugh = True

    # ---------------------------
    # Core update/draw method
    # ---------------------------
    def update(self):
        # Rate limit to frameInterval (ms)
        if millis() - self.fpsTimer < self.frameInterval:
            return
        self.fpsTimer = millis()

        # CURIOUS height offset
        if self.curious:
            if self.eyeLxNext <= 10:
                self.eyeLheightOffset = 8
            elif (self.eyeLxNext >= (self.getScreenConstraint_X() - 10)) and self.cyclops:
                self.eyeLheightOffset = 8
            else:
                self.eyeLheightOffset = 0

            if self.eyeRxNext >= self.screenWidth - self.eyeRwidthCurrent - 10:
                self.eyeRheightOffset = 8
            else:
                self.eyeRheightOffset = 0
        else:
            self.eyeLheightOffset = 0
            self.eyeRheightOffset = 0

        # Left eye height tween
        self.eyeLheightCurrent = (self.eyeLheightCurrent + self.eyeLheightNext + self.eyeLheightOffset) // 2
        # adjust vertical centering when closing/opening
        self.eyeLy += ((self.eyeLheightDefault - self.eyeLheightCurrent) // 2)
        self.eyeLy -= (self.eyeLheightOffset // 2)

        # Right eye height tween
        self.eyeRheightCurrent = (self.eyeRheightCurrent + self.eyeRheightNext + self.eyeRheightOffset) // 2
        self.eyeRy += ((self.eyeRheightDefault - self.eyeRheightCurrent) // 2)
        self.eyeRy -= (self.eyeRheightOffset // 2)

        # Auto-open if previously set to open and fully closed
        if self.eyeL_open:
            if self.eyeLheightCurrent <= 1 + self.eyeLheightOffset:
                self.eyeLheightNext = self.eyeLheightDefault
        if self.eyeR_open:
            if self.eyeRheightCurrent <= 1 + self.eyeRheightOffset:
                self.eyeRheightNext = self.eyeRheightDefault

        # widths tween
        self.eyeLwidthCurrent = (self.eyeLwidthCurrent + self.eyeLwidthNext) // 2
        self.eyeRwidthCurrent = (self.eyeRwidthCurrent + self.eyeRwidthNext) // 2

        # space tween
        self.spaceBetweenCurrent = (self.spaceBetweenCurrent + self.spaceBetweenNext) // 2

        # positions tween
        self.eyeLx = (self.eyeLx + self.eyeLxNext) // 2
        self.eyeLy = (self.eyeLy + self.eyeLyNext) // 2

        # Recompute right eye position from left
        self.eyeRxNext = self.eyeLxNext + self.eyeLwidthCurrent + self.spaceBetweenCurrent
        self.eyeRyNext = self.eyeLyNext
        self.eyeRx = (self.eyeRx + self.eyeRxNext) // 2
        self.eyeRy = (self.eyeRy + self.eyeRyNext) // 2

        # border radius
        self.eyeLborderRadiusCurrent = (self.eyeLborderRadiusCurrent + self.eyeLborderRadiusNext) // 2
        self.eyeRborderRadiusCurrent = (self.eyeRborderRadiusCurrent + self.eyeRborderRadiusNext) // 2

        # Autoblinker
        if self.autoblinker:
            if millis() >= self.blinktimer:
                self.blink_once()
                next_ms = (self.blinkInterval * 1000) + (random.randint(0, self.blinkIntervalVariation) * 1000)
                self.blinktimer = millis() + next_ms

        # Laugh animation
        if self.laugh:
            if self.laughToggle:
                self.setVFlicker(True, 5)
                self.laughAnimationTimer = millis()
                self.laughToggle = False
            elif millis() >= self.laughAnimationTimer + self.laughAnimationDuration:
                self.setVFlicker(False, 0)
                self.laughToggle = True
                self.laugh = False

        # Confused animation
        if self.confused:
            if self.confusedToggle:
                self.setHFlicker(True, 20)
                self.confusedAnimationTimer = millis()
                self.confusedToggle = False
            elif millis() >= self.confusedAnimationTimer + self.confusedAnimationDuration:
                self.setHFlicker(False, 0)
                self.confusedToggle = True
                self.confused = False

        # Idle mode random movement
        if self.idle:
            if millis() >= self.idleAnimationTimer:
                maxx = max(0, self.getScreenConstraint_X())
                maxy = max(0, self.getScreenConstraint_Y())
                # clamp to ints
                self.eyeLxNext = random.randint(0 if maxx <= 0 else 0, maxx) if maxx > 0 else 0
                self.eyeLyNext = random.randint(0 if maxy <= 0 else 0, maxy) if maxy > 0 else 0
                next_ms = (self.idleInterval * 1000) + (random.randint(0, self.idleIntervalVariation) * 1000)
                self.idleAnimationTimer = millis() + next_ms

        # Horizontal and vertical flicker
        if self.hFlicker:
            if self.hFlickerAlternate:
                self.eyeLx += self.hFlickerAmplitude
                self.eyeRx += self.hFlickerAmplitude
            else:
                self.eyeLx -= self.hFlickerAmplitude
                self.eyeRx -= self.hFlickerAmplitude
            self.hFlickerAlternate = not self.hFlickerAlternate

        if self.vFlicker:
            if self.vFlickerAlternate:
                self.eyeLy += self.vFlickerAmplitude
                self.eyeRy += self.vFlickerAmplitude
            else:
                self.eyeLy -= self.vFlickerAmplitude
                self.eyeRy -= self.vFlickerAmplitude
            self.vFlickerAlternate = not self.vFlickerAlternate

        # Cyclops
        if self.cyclops:
            self.eyeRwidthCurrent = 0
            self.eyeRheightCurrent = 0
            self.spaceBetweenCurrent = 0

        # Draw to PIL Image and (if device present) show on device
        img = self.draw_frame_to_image()
        if self.device:
            # luma device expects mode '1' image for monochrome displays
            # Convert if necessary
            if hasattr(self.device, "display"):
                # device.display expects a bitmap; convert to '1' for safety
                self.device.display(img.convert("1"))
            else:
                # unknown device API: try draw directly
                try:
                    self.device.show_image(img)
                except Exception:
                    pass
        else:
            # No device provided — user can use returned image (or save it)
            self._last_image = img

    def draw_frame_to_image(self):
        """Return a PIL Image of the current frame (does not send to device)."""
        mode = "1" if self.monochrome else "L"
        bg = 0 if self.monochrome else 0
        main = 1 if self.monochrome else 255
        img = Image.new(mode, (self.screenWidth, self.screenHeight), color=bg)
        draw = ImageDraw.Draw(img)

        # Draw background (already filled)

        # Draw left eye as rounded rect (center vertically adjusted)
        el_x = int(self.eyeLx)
        el_w = int(self.eyeLwidthCurrent)
        el_h = max(1, int(self.eyeLheightCurrent))
        # vertical centering: adjust top to center the current height inside default eye height
        el_y = int(self.eyeLy + ((self.eyeLheightDefault - el_h) / 2))

        # If width or height could be zero (e.g., cyclops right eye), handle gracefully.
        if el_w > 0 and el_h > 0:
            self._fill_round_rect(draw, el_x, el_y, el_w, el_h, int(self.eyeLborderRadiusCurrent), main)

        # Right eye
        er_x = int(self.eyeRx)
        er_w = int(self.eyeRwidthCurrent)
        er_h = max(0, int(self.eyeRheightCurrent))
        er_y = int(self.eyeRy + ((self.eyeRheightDefault - er_h) / 2))

        if not self.cyclops and er_w > 0 and er_h > 0:
            self._fill_round_rect(draw, er_x, er_y, er_w, er_h, int(self.eyeRborderRadiusCurrent), main)

        # Mood transitions: prepare tired/angry/happy states (eyelids)
        # Tired top eyelids
        if self.tired:
            self.eyelidsTiredHeightNext = self.eyeLheightCurrent // 2
            self.eyelidsAngryHeightNext = 0
        else:
            self.eyelidsTiredHeightNext = 0
        # Angry
        if self.angry:
            self.eyelidsAngryHeightNext = self.eyeLheightCurrent // 2
            self.eyelidsTiredHeightNext = 0
        else:
            self.eyelidsAngryHeightNext = 0
        # Happy bottom offset
        if self.happy:
            self.eyelidsHappyBottomOffsetNext = self.eyeLheightCurrent // 2
        else:
            self.eyelidsHappyBottomOffsetNext = 0

        # Animated transitions (averaging)
        self.eyelidsTiredHeight = (self.eyelidsTiredHeight + self.eyelidsTiredHeightNext) // 2
        self.eyelidsAngryHeight = (self.eyelidsAngryHeight + self.eyelidsAngryHeightNext) // 2
        self.eyelidsHappyBottomOffset = (self.eyelidsHappyBottomOffset + self.eyelidsHappyBottomOffsetNext) // 2

        # Draw tired top eyelids (shape: triangle)
        t = int(self.eyelidsTiredHeight)
        if t > 0:
            # left
            self._fill_triangle(draw,
                                (el_x, el_y - 1),
                                (el_x + el_w, el_y - 1),
                                (el_x, el_y + t - 1),
                                self.BGCOLOR if self.monochrome else 0)
            # right (if not cyclops)
            if not self.cyclops and er_w > 0 and er_h > 0:
                self._fill_triangle(draw,
                                    (er_x, er_y - 1),
                                    (er_x + er_w, er_y - 1),
                                    (er_x + er_w, er_y + t - 1),
                                    self.BGCOLOR if self.monochrome else 0)
            else:
                # cyclops covers split top eyelid halves
                if self.cyclops:
                    half = el_w // 2
                    self._fill_triangle(draw, (el_x, el_y - 1), (el_x + half, el_y - 1), (el_x, el_y + t - 1), self.BGCOLOR)
                    self._fill_triangle(draw, (el_x + half, el_y - 1), (el_x + el_w, el_y - 1), (el_x + el_w, el_y + t - 1), self.BGCOLOR)

        # Draw angry top eyelids
        a = int(self.eyelidsAngryHeight)
        if a > 0:
            if not self.cyclops and er_w > 0 and er_h > 0:
                # left angry triangle (flipped orientation)
                self._fill_triangle(draw,
                                    (el_x, el_y - 1),
                                    (el_x + el_w, el_y - 1),
                                    (el_x + el_w, el_y + a - 1),
                                    self.BGCOLOR if self.monochrome else 0)
                # right angry triangle reversed
                self._fill_triangle(draw,
                                    (er_x, er_y - 1),
                                    (er_x + er_w, er_y - 1),
                                    (er_x, er_y + a - 1),
                                    self.BGCOLOR if self.monochrome else 0)
            else:
                # cyclops split
                half = el_w // 2
                self._fill_triangle(draw, (el_x, el_y - 1), (el_x + half, el_y - 1), (el_x + half, el_y + a - 1), self.BGCOLOR)
                self._fill_triangle(draw, (el_x + half, el_y - 1), (el_x + el_w, el_y - 1), (el_x + half, el_y + a - 1), self.BGCOLOR)

        # Draw happy bottom eyelids - rounded rect under eye
        hb = int(self.eyelidsHappyBottomOffset)
        if hb > 0:
            self._fill_round_rect(draw, el_x - 1, (el_y + el_h) - hb + 1, el_w + 2, self.eyeLheightDefault, int(self.eyeLborderRadiusCurrent), self.BGCOLOR)
            if not self.cyclops and er_w > 0 and er_h > 0:
                self._fill_round_rect(draw, er_x - 1, (er_y + er_h) - hb + 1, er_w + 2, self.eyeRheightDefault, int(self.eyeRborderRadiusCurrent), self.BGCOLOR)

        # Draw sweat drops
        if self.sweat:
            # drop 1 (left)
            if self.sweat1YPos <= self.sweat1YPosMax:
                self.sweat1YPos += 0.5
            else:
                self.sweat1XPosInitial = random.randint(0, 30)
                self.sweat1YPos = 2
                self.sweat1YPosMax = random.randint(10, 20)
                self.sweat1Width = 1.0
                self.sweat1Height = 2.0
            if self.sweat1YPos <= self.sweat1YPosMax / 2:
                self.sweat1Width += 0.5
                self.sweat1Height += 0.5
            else:
                self.sweat1Width = max(1.0, self.sweat1Width - 0.1)
                self.sweat1Height = max(1.0, self.sweat1Height - 0.5)
            self.sweat1XPos = int(self.sweat1XPosInitial - (self.sweat1Width / 2))
            self._fill_round_rect(draw, self.sweat1XPos, int(self.sweat1YPos), max(1, int(self.sweat1Width)), max(1, int(self.sweat1Height)), self.sweatBorderradius, self.MAINCOLOR)

            # drop 2 (center area)
            if self.sweat2YPos <= self.sweat2YPosMax:
                self.sweat2YPos += 0.5
            else:
                self.sweat2XPosInitial = random.randint(30, max(30, self.screenWidth - 30))
                self.sweat2YPos = 2
                self.sweat2YPosMax = random.randint(10, 20)
                self.sweat2Width = 1.0
                self.sweat2Height = 2.0
            if self.sweat2YPos <= self.sweat2YPosMax / 2:
                self.sweat2Width += 0.5
                self.sweat2Height += 0.5
            else:
                self.sweat2Width = max(1.0, self.sweat2Width - 0.1)
                self.sweat2Height = max(1.0, self.sweat2Height - 0.5)
            self.sweat2XPos = int(self.sweat2XPosInitial - (self.sweat2Width / 2))
            self._fill_round_rect(draw, self.sweat2XPos, int(self.sweat2YPos), max(1, int(self.sweat2Width)), max(1, int(self.sweat2Height)), self.sweatBorderradius, self.MAINCOLOR)

            # drop 3 (right)
            if self.sweat3YPos <= self.sweat3YPosMax:
                self.sweat3YPos += 0.5
            else:
                self.sweat3XPosInitial = (self.screenWidth - 30) + random.randint(0, 30)
                self.sweat3YPos = 2
                self.sweat3YPosMax = random.randint(10, 20)
                self.sweat3Width = 1.0
                self.sweat3Height = 2.0
            if self.sweat3YPos <= self.sweat3YPosMax / 2:
                self.sweat3Width += 0.5
                self.sweat3Height += 0.5
            else:
                self.sweat3Width = max(1.0, self.sweat3Width - 0.1)
                self.sweat3Height = max(1.0, self.sweat3Height - 0.5)
            self.sweat3XPos = int(self.sweat3XPosInitial - (self.sweat3Width / 2))
            self._fill_round_rect(draw, self.sweat3XPos, int(self.sweat3YPos), max(1, int(self.sweat3Width)), max(1, int(self.sweat3Height)), self.sweatBorderradius, self.MAINCOLOR)

        return img

    # ---------------------------
    # Low-level drawing helpers
    # ---------------------------
    def _fill_round_rect(self, draw: ImageDraw.ImageDraw, x, y, w, h, r, color):
        """Rounded rectangle (fills). Uses ImageDraw.rounded_rectangle."""
        if w <= 0 or h <= 0:
            return
        # bounding box: left, top, right, bottom
        left = int(x)
        top = int(y)
        right = int(x + w - 1)
        bottom = int(y + h - 1)
        try:
            draw.rounded_rectangle([left, top, right, bottom], radius=max(0, int(r)), fill=color)
        except Exception:
            # fallback: draw rectangle (older Pillow versions)
            draw.rectangle([left, top, right, bottom], fill=color)

    def _fill_triangle(self, draw: ImageDraw.ImageDraw, p1, p2, p3, color):
        """Fill triangle by polygon."""
        pts = [(int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (int(p3[0]), int(p3[1]))]
        draw.polygon(pts, fill=color)

    def display_frame(self, img):
        # Ensure image height fits in the blue region (max 48px)
        if img.height > BLUE_HEIGHT:
            img = img.resize(
                (int(img.width * BLUE_HEIGHT / img.height), BLUE_HEIGHT),
                Image.Resampling.LANCZOS
            )
    
        # Create a blank 128x64 frame
        full_img = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    
        # Center horizontally, but force vertical position inside BLUE ONLY
        x = (DISPLAY_WIDTH - img.width) // 2
        y = BLUE_START_Y  # always draw starting at blue border (16px)
    
        full_img.paste(img, (x, y))
    
        if self.device:
            self.device.display(full_img)



# ---------------------------
# Example usage (main)
# ---------------------------
if __name__ == "__main__":
    # Example for Raspberry Pi using luma.oled
    # pip install luma.oled pillow
    try:
        serial = i2c(port=1, address=0x3C)  # adjust address if needed
        # choose ssd1306 or ssd1327 depending on your OLED
        device = ssd1306(serial, width=128, height=64)
    except Exception as e:
        print("Warning: luma.oled not available or device init failed:", e)
        device = None

    eyes = RoboEyes(device=device, width=128, height=64, frame_rate=50, monochrome=True)

    # Configure some behaviors to demo all animations
    eyes.setDisplayColors(0, 1)
    eyes.setAutoblinker(True, interval=2, variation=3)
    eyes.setIdleMode(True, interval=3, variation=4)
    eyes.setHFlicker(False)
    eyes.setVFlicker(False)
    eyes.setCuriosity(False)
    eyes.setCyclops(False)
    eyes.setSweat(False)

    # Demo loop that randomly triggers animations and moods
    try:
        while True:
            eyes.update()
            
            # Randomly trigger some actions
            r = random.random()
            if r < 0.003:
                eyes.anim_confused()
            elif r < 0.006:
                eyes.anim_laugh()
            elif r < 0.01:
                eyes.setMood(TIRED)
            elif r < 0.012:
                eyes.setMood(ANGRY)
            elif r < 0.014:
                eyes.setMood(HAPPY)
            elif r < 0.016:
                eyes.setMood(DEFAULT)
            elif r < 0.02:
                eyes.setSweat(not eyes.sweat)
            
            img = eyes.draw_frame_to_image()  # generate next animation frame
            eyes.display_frame(img) 
            time.sleep(0.005)  # small sleep to yield
    except KeyboardInterrupt:
        print("Exit")

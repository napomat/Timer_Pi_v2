
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import socket
import sys
import warnings
import subprocess
import re

SRCDIR = "/home/user/epaper_tests"

sys.path.append(os.path.join(SRCDIR, "lib"))

# Suppress GPIO library warning:
with warnings.catch_warnings(action="ignore"):
    from waveshare_epd import epd2in13_V4

def get_ip_address():
    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #try:
        # doesn't even have to be reachable
       # s.connect(('10.255.255.255', 1))
       # local_ip_address = s.getsockname()[0]
    #except:
    #    local_ip_address = '127.0.0.1'
    #finally:
    #    s.close()
    # Führe den Befehl aus, um die Netzwerkinformationen zu bekommen
    result = subprocess.run(['ip', 'a'], stdout=subprocess.PIPE)

    # Holen der Ausgabe als String
    output = result.stdout.decode()

    # Regex für die dynamische IP-Adresse
    # Wir suchen nach einer IP-Adresse mit "dynamic" und "scope global secondary"
    regex = r"inet (\d+\.\d+\.\d+\.\d+/[0-9]+).*scope global.*dynamic"

    # Suche nach der dynamischen IP-Adresse
    ip_address = re.search(regex, output)
    local_ip_address = ip_address.group(1)

    return local_ip_address

picdir = os.path.join(SRCDIR, 'pic')
font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
epd = epd2in13_V4.EPD()
epd.init()
image = Image.new('1', (epd.height, epd.width), 127)
draw = ImageDraw.Draw(image)
draw.text((10, 0), 'IP Address Static', font = font16, fill = 0)
draw.line([10, 20, 213, 20 ], fill=None, width=0, joint=None)
draw.text((10, 18), '192.168.10.175/24', font = font16, fill = 0)
draw.text((10, 38), '10.99.99.250/24', font = font16, fill = 0)
draw.line([10, 90, 213, 90], fill=None, width=0, joint=None)
draw.text((10, 70), 'IP Address dynamic', font = font16, fill = 0)
draw.text((10, 90), f'{get_ip_address()}', font = font24, fill = 0)
inverted = ImageOps.invert(image)
epd.display(epd.getbuffer(image))
epd.sleep()


print("OK")


#!/usr/bin/python3
import os
from datetime import datetime
import random

import logging
from waveshare_epd import epd2in13_V2
from PIL import Image, ImageDraw, ImageFont
import subprocess


logging.basicConfig(level=logging.DEBUG)
picdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pic"
)


def get_data():
    now = datetime.now()
    cputemp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True).stdout

    status = "NORMAL"

    return {
        "date": now.strftime("%b %d, %Y "),
        "time": now.strftime("%I:%M %p "),
        "cputemp": cputemp.decode("utf-8").replace("temp=", ""),
        "status": status,
        "num_ec2s": 9,
    }


def get_updated_image():
    d = get_data()
    logging.info(str(d))
    # Drawing on the image
    font = "GeorgiaBold.ttf"
    fontsm = ImageFont.truetype(font, 16)

    image = Image.new("1", (epd.height, epd.width), 255)  # 255: clear the frame
    logging.info(f"Image dimensions: {epd.height} {epd.width}")
    draw = ImageDraw.Draw(image)

    output = random.choice(("text", "image"))
    print(output)
    if output == "text":
        draw.text(
            (0, 0), " ".join((d["date"], d["time"], d["cputemp"])), font=fontsm, fill=0
        )
        draw.text((0, 20), d["status"], font=fontsm, fill=0)

        lines = [
            f"EC2s: {d['num_ec2s']}, 57%MEM, 37%CPU",
            "DB: 257GB, 57%M",
            "Data: 42 iq, 2456 pending",
            "AiiP: 57%M, 37%",
        ]
        if len(lines) > 4:
            lines = ["ERROR: 4 lines or less"]

        LINE_HEIGHT = 20
        y = 20
        for i, line in enumerate(lines):
            y += LINE_HEIGHT
            print(y, line)
            draw.text((0, y), line, font=fontsm, fill=0)

    elif output == "image":
        icon = Image.open("wolf.jpg")
        image.paste(icon, (0, 0))
    else:
        raise

    return image.rotate(180)


try:
    logging.info("init and Clear")
    epd = epd2in13_V2.EPD()
    epd.init(epd.FULL_UPDATE)
    # epd.Clear(0xFF)
    epd.display(epd.getbuffer(get_updated_image()))

except Exception as e:
    print(e)

finally:
    epd2in13_V2.epdconfig.module_exit()
    exit()

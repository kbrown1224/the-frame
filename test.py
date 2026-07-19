from PIL import Image, ImageDraw
from waveshare_epd.screen import Screen

screen = Screen()
screen.init()

img = Image.new("RGB", (400, 600), "white")
draw = ImageDraw.Draw(img)
draw.rectangle([20, 20, 380, 580], outline="black", width=4)
draw.text((160, 285), "it works", fill="black")

screen.display(screen.getbuffer(img))
screen.sleep()

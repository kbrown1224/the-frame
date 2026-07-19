from PIL import Image, ImageDraw
from waveshare_epd.screen import Screen

screen = Screen()
screen.init()

img = Image.new("RGB", (600, 400), "white")
draw = ImageDraw.Draw(img)
draw.rectangle([20, 20, 580, 380], outline="black", width=4)
draw.text((260, 185), "it works", fill="black")

screen.display(screen.getbuffer(img))
screen.sleep()

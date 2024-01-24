import wx

from PIL import Image

# Open the PNG file
png_image = Image.open('SIS_Icon64.png')

# Convert and save as ICO file
png_image.save('sis_icon.ico')

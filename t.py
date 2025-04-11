# Importing library
import qrcode

# Data to be encoded
data = 'vless://3ff0b0fe-15dd-11f0-a002-60dd8efd8828@5.75.204.10:80?type=tcp#GOD test'

# Encoding data using make() function
img = qrcode.make(data)

# Saving as an image file
img.save('MyQRCode1.png')

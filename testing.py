import base64
from PIL import Image
from io import BytesIO

# Base64 encoded strings of the images
base64_string_1 = "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAQCAYAAAAmlE46AAAAAXNSR0IArs4c6QAAAe5JREFUOI2Nks9rE1EQxz+7+zYlNhoTE61gG4qFEiSBIBgQrRQKgp69evRkz978J9RjD5KLB39gezYVK27pKWq0FbWgBFqtB5OartnNe+NhY6w2igPv8Jj3ed/5zoxVqVSE/4x8Pk+hUCAWi6FE4My5GQ5lj/wDEbyni9RqNdrtNuVyGSUitDuCtDTaDMaUI3RCoVgskkqlqVYXUSKGoCsQCGFXSCdscllFJxReN0IAhhxB68jRxMRxEolhlDGCERARRg7aHE2p6LFrURqPUf/YQQCtNZ7n4XleVIVI9FMu63Igbu0p0xjodruUytNMTc/gOhaWBcoYAyKsbwYEXT3Qo21ZbH83+KFgW+DYVqRoekebwZPRQKh/5ZRjR4rS8yh/Af8MseUnKBgT+QEQBC0hrXADG0VCZVD2UB+Mu71SBTDGoLVmO/zMm9YjVrZuY7tRs5LOMUqpS4wnTpPLpJkcjfcUo/6w4a9Rbz7kfftxHwJo6gZLX25yOOszOXp59ziErc5bXjYfsN5+MtDXlZPXmBq7AMBOQLQA34Kv1P0FPuwsD4Sun71FPlMCYKXxjOq7pWjllj/doWG/QkuwB7px/j6ZfSMA3Fub4+7qHPvdDMr3feznw4xx6jcgmUwyO3u1f5+fX2D1xSYnuAjADypl+Yqeo906AAAAAElFTkSuQmCC"
base64_string_2 = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAj1JREFUOI2NkU1IlFEUhp/7zTfzaWmTNppCKpYhEkpD0ECUNSAEtW7bKlvlul37tv0sXZibDCtSW6Zh4YgrK0NDEgpJyxbq/P/cc1p8OlJO0YG7uPfyvLzve8zw8LDyn9PV1UV3dzehUKj85qrC+Yt9HGk4+g9USbydYn5+nnQ6TSwWw/O8XQElnVd022KlMu4GlHxR6enpoa6unsnJKeLxS1RVVeGoCoWSkikoqZwQcuFks0trJEAqJ6RyQjYnWOsn7eg4QTR6momJCTKZDK6IIgqqStNhh+Y6FwAvaIi2h1j4mkcBay2JRIJEIgGAMYaRkSd+BIC2hiCHqs0++yJQKpWIxuL0xvsIBgzGQD6b4eXYKK6IgCor6wUKJVuxA8cYkjkhW1QcAwHH4FhBRHwHsnOsVN6oBYp2788NOHhGUVXfge50oH8R+HPUUWoO1dLff2NXQBHx8wIoitUi28U1HFxq3Aiu45UFqoOG440B342qooCIYK0lWfzBp+1XzG0M4QT9UsOBY0TrrtFec462SD2dLdV7cUQE9XtkLbvEwtYLPqdfl2GALbvKm58PaGzI0tlyHYBkMsnQ0KPdNSob+WU+bD1nJT1dMffNM7fpbb0CQKYAy2slVBVHREkVNlnYHOdLZrYifOfCwzI8tzrDvZm7/uZEcVWF2e+PWXU+YrWwD75/+RmRA00APF0aZHRxkNpghOlvLuDgZrNZnHcHaeXsb2A4HGZg4Fb5PjY2zuL7dU5x1Y9hcniexy9VCihtv/sVygAAAABJRU5ErkJggg=="

# Decode base64 strings to images
def decode_base64_to_image(base64_string):
    decoded = base64.b64decode(base64_string)
    return Image.open(BytesIO(decoded))

# Resize images to a common size (16x16)
def resize_image(image, size=(16, 16)):
    return image.resize(size, Image.ANTIALIAS)

# Function to compare two images pixel by pixel
def images_are_equal(image1, image2):
    return image1.tobytes() == image2.tobytes()

# Decode images
image1 = decode_base64_to_image(base64_string_1)
image2 = decode_base64_to_image(base64_string_2)

# Resize images
image1_resized = resize_image(image1)
image2_resized = resize_image(image2)

# Compare resized images
if images_are_equal(image1_resized, image2_resized):
    print("The images have the same content despite different dimensions.")
else:
    print("The images have different content.")

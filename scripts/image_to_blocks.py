from PIL import Image

def image_to_blocks(image_path, width=100):
    img = Image.open(image_path)
    img = img.convert('RGB')
    aspect_ratio = img.height / img.width
    new_height = int(aspect_ratio * width * 0.55)
    img = img.resize((width, new_height))

    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            print(f"\033[48;2;{r};{g};{b}m  ", end="")
        print("\033[0m")

image_to_blocks('/home/seane/Development/dixit/data/image.png')
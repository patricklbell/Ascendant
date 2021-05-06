import sys
from PIL import Image

if not len(sys.argv) == 3:
    print("Incorrect number of arguments, expected: input.png output.json")
    sys.exit()

try:
    open(sys.argv[1], 'rb')
except:
    print("Invalid input file: ", sys.argv[1])
    sys.exit()

image = Image.open(sys.argv[1]) 
px = image.load() 

px_excluded = []

rectangles = []

width, height = image.size
for x in range(width-1):
    for y in range(height-1):
        if not [x, y] in px_excluded:
            if not px[x,y] == (255,255,255,255):
                print(f"reactangle began at {x, y}")
                box_height = 1
                box_width = 1
                
                box_x = 0
                for box_x in range(width - x - 1):
                    if not px[x+box_x,y] == (255,255,255,255):
                        box_width+=1
                    else:
                        break
                
                box_y = 0
                for box_y in range(height - y - 1):
                    if not px[x,y+box_y] == (255,255,255,255):
                        box_height+=1
                        for i in range(box_width):
                            px_excluded.append([x+i, y+box_y])
                    else:
                        break
                print(f"reactangle h, w: {box_width, box_height}")
                rectangles.append({"x": x, "y":y, "width":box_width, "height":box_height})

print(rectangles)
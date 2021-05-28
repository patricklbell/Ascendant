# Script to automate converting tmx files into images and entity files, not run by game
import os, subprocess, tempfile, json
import xml.etree.ElementTree as ET

SRC_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "")
TMX_RASTERIZER = f"{SRC_DIRECTORY}.tools\\Tiled\\tmxrasterizer.exe"
IMAGE_TO_ENTITIES = f"{SRC_DIRECTORY}.tools\\image_to_entities\\image_to_entities.exe"

def proccess_level_directory(name):
    level_file = f"{name}\\level.tmx"
    print(level_file)
    level_data = ET.parse(level_file).getroot()
    for group in level_data.findall("group"):
        grp_name, grp_id = group.attrib["name"], group.attrib["id"]
        
        # Determine layer names
        lyr_names = []
        for layer in group.findall("layer"):
            lyr_names.append(layer.attrib["name"])

        if grp_name == "Entities":
            entities = {}
            for lyr_name in lyr_names:
                tmp_lyr_fname = tempfile.gettempdir()+f"\\a7d89a.bmp"
                output = subprocess.call([TMX_RASTERIZER, level_file, tmp_lyr_fname, "--show-layer", lyr_name, "--ignore-visibility"])
                if not output == 0:
                    print("Error rasterising with command: ")
                    print(*[TMX_RASTERIZER, level_file, tmp_lyr_fname, "--show-layer", lyr_name, "--ignore-visibility"])
                
                buf = subprocess.Popen([IMAGE_TO_ENTITIES, tmp_lyr_fname],stdout=subprocess.PIPE).stdout.read()
                try:
                    entities_json = json.loads(buf.decode("ascii"))
                    entities[lyr_name] = entities_json
                except:
                    print("error decoding image to entities output")
                    print(*[IMAGE_TO_ENTITIES, tmp_lyr_fname])
            
            # Write entities file
            json_fname = f"{name}\\entities.json"
            with open(json_fname, 'w') as f:
                json.dump(entities, f)

        else:
            args = ["--ignore-visibility"]
            for lyr_name in lyr_names:
                args += ["--show-layer", lyr_name]
            output = subprocess.call([TMX_RASTERIZER, level_file, f"{name}\\{grp_name}.png"]+args)
            if not output == 0:
                print("Error rasterising with command: ")
                print(*([TMX_RASTERIZER, level_file, f"{name}\\{grp_name}.png"] + args), sep=" ")

if __name__ == "__main__":
    for name in [x[0] for x in os.walk(".")]:
        if len(name) > 1 and not name[2] == ".":
            proccess_level_directory(name)
#include <iostream>
#include <fstream>
#include <string>
#include "bitmap_image.hpp"

int main(int argc, char **argv){
    // Input checking
    if(argc != 2){
        std::cout << "Error - Expected arguments: input.bmp" << std::endl;
        return 1;
    }
    char* input_filename = argv[1];
    bitmap_image image(input_filename);
    if (!image)
    {
        std::cout << "Error - Failed to open: " << input_filename << std::endl;
        return 1;
    }

    std::ofstream output;
    // output.open(argv[2], std::ios::trunc);

    const unsigned int height = image.height();
    const unsigned int width  = image.width();

    bool *px_unused = (bool*)malloc(sizeof *px_unused * height * width);

    // std::string colliders = "", players = "", enemies = "", flying_enemies = "", transitions = "", water = "", save_game = "", damage_colliders = "";
    std::string json;


    for (std::size_t y = 0; y < height-1; ++y)
    {
        for (std::size_t x = 0; x < width; ++x)
        {
            if(px_unused[y*width + x] == false){
                rgb_t colour, og_colour;

                image.get_pixel(x, y, colour);

                image.get_pixel(x, y, og_colour);

                // Check if pixels isn't black
                if (colour.red > 0 || colour.green > 0 || colour.blue > 0){
                    int box_x=0, box_y=0;
                    for(; box_x < (width-x); ++box_x){
                        image.get_pixel(x+box_x, y, colour);
                        if (
                            (colour.red == 0 && colour.green == 0 && colour.blue == 0) ||
                            (colour.red != og_colour.red || colour.green != og_colour.green || colour.blue != og_colour.blue)){
                            break;
                        }
                    }

                    for(; box_y < (height-y); ++box_y){
                        for(unsigned int i = 0; i < box_x; ++i){
                            image.get_pixel(x+i, y+box_y, colour);
                            if (
                                (colour.red == 0 && colour.green == 0 && colour.blue == 0) || 
                                (colour.red != og_colour.red || colour.green != og_colour.green || colour.blue != og_colour.blue)){
                                ++box_y;
                                goto endofloop;
                            }
                        }
                    }
                    endofloop:

                    for(int i = 0; i < box_x; ++i){
                        for(int j = 0; j < box_y; ++j){
                            px_unused[(y+j)*width + x+i] = true;
                            //std::cout << y+j << ", " << x+i << "; ";
                        }
                    }

                    image.get_pixel(x, y, colour);
                    // std::cout << x << ", " << y << "; " << box_x << ", " << box_y << std::endl;
                    json += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + ", \"width\":" + std::to_string(box_x) + ", \"height\":" + std::to_string(box_y) + "},";
                    // Entities
                    // if ((int)colour.red == 255) enemies += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + "},";
                    // if ((int)colour.red == 254) flying_enemies += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + "},";
                    // if ((int)colour.blue == 255) players += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + "},";
                    // if ((int)colour.blue == 254) transitions += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + ", \"width\":" + std::to_string(box_x) + ", \"height\":" + std::to_string(box_y) + "},";
                    // if ((int)colour.blue == 253) save_game += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + ", \"width\":" + std::to_string(box_x) + ", \"height\":" + std::to_string(box_y) + "},";
                    // if ((int)colour.green == 255) colliders += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + ", \"width\":" + std::to_string(box_x) + ", \"height\":" + std::to_string(box_y) + "},";
                    // if ((int)colour.green == 254) water += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + ", \"width\":" + std::to_string(box_x) + ", \"height\":" + std::to_string(box_y) + "},";
                    // if ((int)colour.green == 253) damage_colliders += "{\"x\":" + std::to_string(x) + ", \"y\":" + std::to_string(y) + ", \"width\":" + std::to_string(box_x) + ", \"height\":" + std::to_string(box_y) + "},";
                }
            }
        }
    }
    // Remove trailing commas
    // std::string str_array[] = {colliders, players, enemies, flying_enemies, water, transitions, save_game, damage_colliders};
    // for(auto& str: str_array){
    //     if (str.length() >= 1){
    //         str[str.length()-1] = ' ';
    //     }
    // }

    // std::string name(argv[1]);
    // std::replace( name.begin(), name.end(), '\\', '/');

    // output << "{ \"name\":\"" << name.substr(2, name.length()-1) << "\", \"collisions\":[" << str_array[0] << "] " << ", \"save_games\":[" << str_array[6] << "]" << ", \"damage_colliders\":[" << str_array[7] << "]"<< ", \"transitions\":[" << str_array[5] << "] " << ", \"players\":[" << str_array[1] << "] " << ", \"enemies\":[" << str_array[2] << "]" << ", \"flying_enemies\":[" << str_array[3] << "]" << ", \"water\":[" << str_array[4] << "]}";

    if (json.length() > 1){
        json[json.length()-1]=' ';
    }
    std::cout << "[" << json << "]";
    return 0;
}
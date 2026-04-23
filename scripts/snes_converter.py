import os
from collections import namedtuple
from typing import List

Color = namedtuple('Color', ['r', 'g', 'b'])

def to_snes_color(r, g, b):
    # Convert 8-bit to 5-bit
    r5 = r >> 3
    g5 = g >> 3
    b5 = b >> 3
    # SNES format: 0BBBBBGGGGGRRRRR (little-endian)
    return (b5 << 10) | (g5 << 5) | r5

def write_palette_asm(colors: List[Color], bpp: int, output_path: str, label: str):
    colors_per_palette = 1 << bpp
    num_palettes = (len(colors) + colors_per_palette - 1) // colors_per_palette

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(".segment \"RODATA\"\n\n")
        f.write("; Automatically generated palette data\n")
        f.write(f"; SNES BPP: {bpp} ({colors_per_palette} colors per palette)\n")
        f.write(f"; Total colors: {len(colors)}\n\n")
        
        f.write(f".export {label}\n")
        f.write(f"{label}:\n")
        for i in range(num_palettes):
            palette_slice = colors[i * colors_per_palette : (i + 1) * colors_per_palette]
            f.write(f"  {label}_{i}:\n")
            for j, color in enumerate(palette_slice):
                snes_color = to_snes_color(color.r, color.g, color.b)
                f.write(f"    .word ${snes_color:04x} ; color {j:2}: (R:{color.r:3}, G:{color.g:3}, B:{color.b:3})\n")
            
            if len(palette_slice) < colors_per_palette:
                for j in range(len(palette_slice), colors_per_palette):
                    f.write(f"    .word $0000 ; color {j:2}: (padding)\n")
            f.write("\n")

def convert_to_snes_tile(pixel_data, bpp):
    tile_data = []
    for y in range(8):
        plane0, plane1 = 0, 0
        for x in range(8):
            color_idx = pixel_data[y][x]
            plane0 |= ((color_idx >> 0) & 1) << (7 - x)
            plane1 |= ((color_idx >> 1) & 1) << (7 - x)
        tile_data.extend([plane0, plane1])
    
    if bpp >= 4:
        for y in range(8):
            plane2, plane3 = 0, 0
            for x in range(8):
                color_idx = pixel_data[y][x]
                plane2 |= ((color_idx >> 2) & 1) << (7 - x)
                plane3 |= ((color_idx >> 3) & 1) << (7 - x)
            tile_data.extend([plane2, plane3])
            
    if bpp >= 8:
        for y in range(8):
            plane4, plane5 = 0, 0
            for x in range(8):
                color_idx = pixel_data[y][x]
                plane4 |= ((color_idx >> 4) & 1) << (7 - x)
                plane5 |= ((color_idx >> 5) & 1) << (7 - x)
            tile_data.extend([plane4, plane5])
        for y in range(8):
            plane6, plane7 = 0, 0
            for x in range(8):
                color_idx = pixel_data[y][x]
                plane6 |= ((color_idx >> 6) & 1) << (7 - x)
                plane7 |= ((color_idx >> 7) & 1) << (7 - x)
            tile_data.extend([plane6, plane7])
            
    return tile_data

def write_tiles_asm(image_data, bpp, output_path, label):
    width, height = image_data.width, image_data.height
    tiles_x, tiles_y = width // 8, height // 8
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(".segment \"CHRMAP\"\n\n")
        f.write("; Automatically generated tile data\n")
        f.write(f"; Width: {width}, Height: {height}, BPP: {bpp}\n\n")
        f.write(f".export {label}\n")
        f.write(f"{label}:\n")

        for ty in range(tiles_y):
            for tx in range(tiles_x):
                pixel_grid = [image_data.data[ty*8 + y][tx*8 : tx*8 + 8] for y in range(8)]
                snes_tile = convert_to_snes_tile(pixel_grid, bpp)
                f.write(f"  ; Tile ({tx}, {ty})\n")
                for i in range(0, len(snes_tile), 8):
                    for byte in [f"%{b:08b}" for b in snes_tile[i:i+8]]:
                        f.write(f"    .byte {byte}\n")
                f.write("\n")
        f.write(f"{label}_END:\n")

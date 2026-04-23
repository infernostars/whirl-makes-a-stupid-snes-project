import sys
import os

# Add the project root to sys.path to allow importing libaseprite and snes_converter
sys.path.append(os.getcwd())

from scripts.libaseprite import AsepriteFile
from scripts.libaseprite.chunks import OldPaleteChunk_0x0004, OldPaleteChunk_0x0011, PaletteChunk
from scripts.libaseprite.blitframe import merge_frame_cels
from scripts.snes_converter import Color, write_palette_asm, write_tiles_asm

def extract_colors(parsed_file: AsepriteFile):
    colors = []
    for frame in parsed_file.frames:
        for chunk in frame.chunks:
            if isinstance(chunk, (OldPaleteChunk_0x0004, OldPaleteChunk_0x0011)):
                for packet in chunk.packets:
                    for color in packet['colors']:
                        colors.append(Color(color[0], color[1], color[2]))
                if colors: return colors
            elif isinstance(chunk, PaletteChunk):
                for color in chunk.colors:
                    colors.append(Color(color['red'], color['green'], color['blue']))
                if colors: return colors
    return colors

def main():
    # Configuration for characters
    assets_config = [
        {
            "input": "src/assets/characters.aseprite",
            "palette_out": "src/generated/palette.asm",
            "tiles_out": "src/generated/tiles.asm",
            "bpp": 2,
            "label": "CHARACTER"
        }
    ]

    for config in assets_config:
        input_path = config["input"]
        if not os.path.exists(input_path):
            print(f"Skipping {input_path}: Not found.")
            continue

        with open(input_path, 'rb') as f:
            parsed_file = AsepriteFile(f.read())
        
        # 1. Palette
        colors = extract_colors(parsed_file)
        if colors:
            write_palette_asm(colors, config["bpp"], config["palette_out"], f"{config['label']}_PALETTE")
            print(f"Saved palette to {config['palette_out']}")

        # 2. Tiles
        merged_image = merge_frame_cels(parsed_file, 0, parsed_file.header.palette_mask)
        write_tiles_asm(merged_image, config["bpp"], config["tiles_out"], f"{config['label']}_TILES")
        print(f"Saved tiles to {config['tiles_out']}")

if __name__ == "__main__":
    main()

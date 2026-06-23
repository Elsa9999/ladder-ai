# -*- coding: utf-8 -*-
import os
import struct

def inspect_png(file_path):
    print(f"Checking: {file_path}")
    if not os.path.exists(file_path):
        print("  Error: File does not exist!")
        return
    
    size = os.path.getsize(file_path)
    print(f"  File Size: {size} bytes ({size / 1024 / 1024:.2f} MB)")
    
    with open(file_path, "rb") as f:
        sig = f.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            print("  Error: Invalid PNG signature!")
            print(f"  Header bytes: {sig.hex()}")
            return
            
        # Read IHDR chunk
        # Chunk size (4 bytes), Chunk type (4 bytes - should be IHDR), Width (4 bytes), Height (4 bytes)
        ihdr_len_bytes = f.read(4)
        ihdr_type = f.read(4)
        if ihdr_type != b"IHDR":
            print(f"  Error: Expected IHDR chunk, got {ihdr_type}")
            return
            
        width_bytes = f.read(4)
        height_bytes = f.read(4)
        
        width = struct.unpack(">I", width_bytes)[0]
        height = struct.unpack(">I", height_bytes)[0]
        
        print(f"  Dimensions: {width} x {height}")
        print("  PNG signature and IHDR chunk are VALID.")

inspect_png(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\exported_bg_graphic files\DefaultImageStream.png")
inspect_png(r"D:\AI_Agent_PLC_LADDER_ONLY\scratch\exported_bg_graphic files\ImageStream.png")

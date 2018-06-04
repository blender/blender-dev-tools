
import os
PATHS = (
    "release/scripts/modules",
    "release/scripts/startup",
    "source/blender/bmesh",
    "source/blender/draw",  # blender2.8 branch only.
    "source/blender/editors/interface",
    "source/blender/editors/transform",
    "source/blender/gpu",
    "source/blender/python",
)

SOURCE_DIR = os.path.normpath(os.path.abspath(os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".."))))

PATHS = tuple(os.path.join(SOURCE_DIR, p) for p in PATHS)

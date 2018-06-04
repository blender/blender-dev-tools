
import os
PATHS = (
    "intern/ghost",
    "release/scripts/modules",
    "release/scripts/startup",
    "source/blender/bmesh",
    "source/blender/draw",  # blender2.8 branch only.
    "source/blender/editors",
    "source/blender/gpu",
    "source/blender/python",
    "tests",
)

SOURCE_DIR = os.path.normpath(os.path.abspath(os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".."))))

PATHS = tuple(
    os.path.join(SOURCE_DIR, p.replace("/", os.sep))
    for p in PATHS
)

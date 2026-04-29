import numpy as np
import pytest
from PIL import Image
from pathlib import Path
import tempfile, os

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff',
                        '.cr2', '.cr3', '.arw', '.nef', '.dng', '.orf', '.rw2'}

@pytest.fixture
def tmp_image_folder(tmp_path):
    """Creates a folder with 5 small JPEG test images."""
    for i in range(1, 6):
        img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8))
        img.save(tmp_path / f"IMG_{i:04d}.jpg")
    return tmp_path

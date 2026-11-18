
from pathlib import Path
from io import BytesIO
import subprocess
from config import root_path

from PIL import Image


def generate_icon():

    assets_path = root_path / "assets"

    svg_path = assets_path / "mariadb_manager.svg"
    png_path = assets_path / "icon.png"
    ico_path = assets_path / "icon.ico"

    inkscape = Path(
        r"C:\Program Files\Inkscape\bin\inkscape.exe"
    )

    ico_sizes = [
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256)
    ]

    subprocess.run(
        [
            str(inkscape),
            str(svg_path),
            "--export-filename=" + str(png_path),
            "--export-width=512",
            "--export-height=512"
        ],
        check=True
    )

    with Image.open(png_path) as image:
        image.save(
            ico_path,
            format="ICO",
            sizes=ico_sizes
        )

    png_path.unlink()

    print(f"Icon generated: {ico_path}")


if __name__ == "__main__":
    generate_icon()
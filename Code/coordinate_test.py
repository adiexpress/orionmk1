#running a small test run to see if everything works

from conversion import load_homo_matrix, pixel_conversion
import json

H = load_homo_matrix()

with open ("calibration.json", "r") as file:
    data = json.load(file)

pixel_points = data["pixel_points"]
real_world_points = data["real_world_points"]

print(f"{'pixel': <20} {'Expected': <20} {'Actual': <20} {'Error'}")

for i, (pixel, expected) in enumerate(zip(pixel_points, real_world_points)):
    px, py = pixel
    ex, ey = expected

    actual_x, actual_y = pixel_conversion(px, py, H)

    error_x = round(abs(actual_x - ex), 2)
    error_y = round(abs(actual_y - ey), 2)

    print(f"({int(px)}, {int(py)}) {'': <10} ({ex}, {ey}){'':<12} ({actual_x}, {actual_y}){'':<10} x+- {error_x}cm y+- {error_y}cm")


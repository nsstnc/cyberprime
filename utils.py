from database.database import database
import os


async def get_results_message() -> str:
    fractions_points = await database.get_fractions_points()
    print(fractions_points)
    text = ""
    for fraction_id, fraction_name, points in sorted(fractions_points, key=lambda x: x[2], reverse=True):
        text += f"\n{fraction_name}: {points}"
    return text


async def get_absolute_path(file_path):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.normpath(os.path.join(BASE_DIR, file_path))
    return abs_path



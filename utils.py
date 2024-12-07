from database.database import database


async def get_results_message() -> str:
    fractions_points = await database.get_fractions_points()
    print(fractions_points)
    text = ""
    for fraction_id, fraction_name, points in sorted(fractions_points, key=lambda x: x[2], reverse=True):
        text += f"\n{fraction_name}: {points}"
    return text

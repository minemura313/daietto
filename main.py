from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DietRequest(BaseModel):
    gender: str          # "male" または "female"
    age: int
    height: float
    weight: float
    activityLevel: float # 1.2, 1.375, 1.55, 1.725, 1.9
    targetKg: float
    targetMonths: float

@app.post("/api/v1/calculate-diet")
def calculate_diet(data: DietRequest):
    # 1. BMR（Ganpuleの式）
    gender_const = 0.5473 if data.gender == "male" else 1.0946
    bmr = round(((0.1238 + (0.0481 * data.weight) + (0.0234 * data.height) - (0.0138 * data.age) - gender_const) * 1000) / 4.186)

    # 2. TDEE
    tdee = round(bmr * data.activityLevel)

    # 3. 目標カロリー & BMRガード
    daily_deficit = (data.targetKg * 7200) / (data.targetMonths * 30) if data.targetMonths > 0 else 0
    target_calories = round(tdee - daily_deficit)
    is_bmr_guarded = False

    if target_calories < bmr:
        target_calories = bmr
        is_bmr_guarded = True

    # 4. PFC
    p_grams = round(data.weight * 2.0 if data.gender == "male" else data.weight * 1.5)
    p_cal = p_grams * 4

    f_cal = round(target_calories * 0.20)
    f_grams = round(f_cal / 9)

    c_cal = max(0, target_calories - (p_cal + f_cal))
    c_grams = round(c_cal / 4)

    return {
        "status": "success",
        "data": {
            "bmr": bmr,
            "tdee": tdee,
            "targetCalories": target_calories,
            "isBmrGuarded": is_bmr_guarded,
            "pfc": {
                "protein": {"grams": p_grams, "calories": p_cal},
                "fat": {"grams": f_grams, "calories": f_cal},
                "carbs": {"grams": c_grams, "calories": c_cal}
            }
        }
    }

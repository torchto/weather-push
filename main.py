import requests
import os

def get_access_token():
    appid = os.getenv("APPID")
    secret = os.getenv("APPSECRET")
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    res = requests.get(url).json()
    return res.get("access_token")

def get_weather():
    key = os.getenv("WEATHER_KEY")
    city = os.getenv("CITY")
    url = f"https://devapi.qweather.com/v7/weather/3d?location={city}&key={key}"
    res = requests.get(url).json()
    day = res["daily"][1]
    return {
        "date": day["fxDate"],
        "weather": day["textDay"],
        "tempMin": day["tempMin"],
        "tempMax": day["tempMax"],
    }

def make_clothes(tempMax, weather):
    t = int(tempMax)
    if t < 10:
        s = "❄️ 寒冷，建议羽绒服+毛衣+秋裤"
    elif t < 20:
        s = "☁️ 微凉，建议外套+长袖"
    elif t < 28:
        s = "☀️ 舒适，薄外套或针织衫"
    else:
        s = "🔥 炎热，短袖短裤，注意防晒"
    if "雨" in weather:
        s += "，记得带伞"
    return s

def send_message(token, weather, clothes):
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    data = {
        "touser": os.getenv("OPENID"),
        "template_id": os.getenv("TEMPLATE_ID"),
        "data": {
            "first": {"value": "🌤️ 明日天气及穿衣建议"},
            "city": {"value": os.getenv("CITY_NAME")},
            "date": {"value": weather["date"]},
            "weather": {"value": weather["weather"]},
            "temp": {"value": f"{weather['tempMin']}~{weather['tempMax']}℃"},
            "clothes": {"value": clothes},
            "remark": {"value": "天气多变，注意增减衣物~"}
        }
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    weather = get_weather()
    clothes = make_clothes(weather["tempMax"], weather["weather"])
    token = get_access_token()
    send_message(token, weather, clothes)

import requests
import os

def get_access_token():
    appid = os.getenv("APPID")
    appsecret = os.getenv("APPSECRET")
    
    if not appid or not appsecret:
        print("❌ APPID 或 APPSECRET 未配置")
        return None

    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"
    try:
        res = requests.get(url, timeout=10).json()
        token = res.get("access_token")
        if token:
            print("✅ 获取 access_token 成功")
        else:
            print("❌ 获取 token 失败：", res)
        return token
    except Exception as e:
        print("❌ 请求 token 失败：", e)
        return None

def get_weather():
    key = os.getenv("WEATHER_KEY")
    city = os.getenv("CITY")

    if not key or not city:
        print("❌ 天气配置缺失")
        return None

    # ✅ 已经用你专属的 API Host
    url = f"https://jq4t2cc795.re.qweatherapi.com/v7/weather/3d?location={city}&key={key}"
    
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("code") != "200":
            print("❌ 天气API错误：", res)
            return None

        day = res["daily"][1]
        weather_data = {
            "date": day["fxDate"],
            "weather": day["textDay"],
            "tempMin": day["tempMin"],
            "tempMax": day["tempMax"],
        }
        print("✅ 获取天气成功：", weather_data)
        return weather_data
    except Exception as e:
        print("❌ 获取天气失败：", e)
        return None

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
    openid = os.getenv("OPENID")
    template_id = os.getenv("TEMPLATE_ID")
    city_name = os.getenv("CITY_NAME")

    if not token:
        print("❌ 无 token，无法发送")
        return
    if not openid or not template_id:
        print("❌ OPENID 或 TEMPLATE_ID 未配置")
        return

    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    
    data = {
        "touser": openid,
        "template_id": template_id,
        "data": {
            "first": {"value": "🌤️ 明日天气及穿衣建议"},
            "city": {"value": city_name},
            "date": {"value": weather["date"]},
            "weather": {"value": weather["weather"]},
            "temp": {"value": f"{weather['tempMin']}~{weather['tempMax']}℃"},
            "clothes": {"value": clothes},
            "remark": {"value": "天气多变，注意增减衣物"}
        }
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        print("✅ 微信返回结果：", result)
        if result.get("errcode") == 0:
            print("🎉 微信消息发送成功！")
        else:
            print("❌ 微信发送失败：", result)
    except Exception as e:
        print("❌ 发送请求失败：", e)

if __name__ == "__main__":
    print("=== 开始运行 ===")
    weather = get_weather()
    if not weather:
        exit(1)

    clothes = make_clothes(weather["tempMax"], weather["weather"])
    token = get_access_token()
    send_message(token, weather, clothes)

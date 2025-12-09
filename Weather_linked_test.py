import requests
import json
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS


#도시별 위도/경도
seoul_gu_coords = {
    '강남구': {'lat': 37.517236, 'lon': 127.047325},
    '강동구': {'lat': 37.530125, 'lon': 127.123762},
    '강북구': {'lat': 37.639610, 'lon': 127.025657},
    '강서구': {'lat': 37.550980, 'lon': 126.849538},
    '관악구': {'lat': 37.478406, 'lon': 126.951613},
    '광진구': {'lat': 37.538561, 'lon': 127.082381},
    '구로구': {'lat': 37.495403, 'lon': 126.887369},
    '금천구': {'lat': 37.456881, 'lon': 126.895229},
    '노원구': {'lat': 37.654259, 'lon': 127.056294},
    '도봉구': {'lat': 37.668884, 'lon': 127.047151},
    '동대문구': {'lat': 37.574484, 'lon': 127.039921},
    '동작구': {'lat': 37.512402, 'lon': 126.939538},
    '마포구': {'lat': 37.566196, 'lon': 126.901615},
    '서대문구': {'lat': 37.579116, 'lon': 126.936778},
    '서초구': {'lat': 37.483712, 'lon': 127.032411},
    '성동구': {'lat': 37.563332, 'lon': 127.037120},
    '성북구': {'lat': 37.589116, 'lon': 127.018214},
    '송파구': {'lat': 37.514544, 'lon': 127.106597},
    '양천구': {'lat': 37.516988, 'lon': 126.866002},
    '영등포구': {'lat': 37.526372, 'lon': 126.896228},
    '용산구': {'lat': 37.532561, 'lon': 127.008605},
    '은평구': {'lat': 37.602758, 'lon': 126.929164},
    '종로구': {'lat': 37.572950, 'lon': 126.979358},
    '중구': {'lat': 37.564090, 'lon': 126.997940},
    '중랑구': {'lat': 37.606308, 'lon': 127.092479}
    }

#당일 날씨 관련 데이터 반환
def now_get_weather(city_name):

    #OpenWeather 데이터 호출값
    openweather_url = 'https://api.openweathermap.org/data/2.5/weather'
    openweather_api_key = '863577c3e6d70d7c15a60624a59fdf00'
    
    city_name = city_name.strip()
    coords = seoul_gu_coords[city_name]

    openweather_params = {
        'lat': coords['lat'],
        'lon': coords['lon'],
        'appid': openweather_api_key,
        'units': 'metric',
        'lang': 'kr'
    }
    
    #openweather에서 반환값 받기
    openweather_response = requests.get(openweather_url, params=openweather_params, timeout=10)
    
    #반환값 적절성 판단
    if openweather_response.status_code == 200 :
        openweather_data = openweather_response.json()
        return openweather_data
    else :
        print('Error:', openweather_response.status_code)
        return None
    



def now_get_dust(city_name) : 
    #한국환경공단 데이터 호출값(미세먼지, 오존)
    dust_url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
    dust_api_key = 'a2f8c0054fcb8adcd1da40e042d50a736e3eaceb7ad47fb611aca695e898820c'

    city_name = city_name.strip()
    coords = seoul_gu_coords[city_name]

    dust_params = {
        'serviceKey' : dust_api_key,
        'returnType' : 'json',
        'numOfRows' : 1,
        'pageNo' : 1,
        'stationName' : city_name,
        'dataTerm' : 'DAILY',       
        'ver' : '1.3',              
    }

    #한국환경공단에서 반환값 받기 
    try:
        dust_response = requests.get(dust_url, params=dust_params, timeout=10)
    except requests.exceptions.RequestException as err_request:
        print('요청 실패:', err_request)
        return None

    #반환값 적절성 판단
    if dust_response.status_code == 200:
        try:
            dust_data = dust_response.json()
        except ValueError:
            print('Error: 응답을 JSON으로 파싱하지 못했습니다. 전체응답:', dust_response.text[:2000])
            return None
        return dust_data
    else:
        print('Error: HTTP', dust_response.status_code)
        return None

final_data={}


city_name = ("강북구")

try:
    today_weather_data = now_get_weather(city_name)
    today_dust_data = now_get_dust(city_name)

    total_data=today_weather_data | today_dust_data
    final_data={'main':total_data['weather'][0]['main'],
            'temp':total_data['main']['temp'],
            'feels_like':total_data['main']['feels_like'],
            'temp_min':total_data['main']['temp_min'],
            'temp_max':total_data['main']['temp_max'],
            'humidity':total_data['main']['humidity'],
            'wind_speed':total_data['wind']['speed'],
            'wind_degree':total_data['wind']['deg'],
            'o3grade':total_data['response']['body']['items'][0]['o3Grade'],
            'pm10value':total_data['response']['body']['items'][0]['pm10Value'],
            'pm25value':total_data['response']['body']['items'][0]['pm25Value']}
    # print(final_data)
except:
    print("Error : NOT IN SEOUL_GU_COORDS")

    

# print(final_data)


    # if today_weather_data and today_dust_data:
    #     print(f"{today_weather_data}\n\n\n")
    #     print(today_dust_data)


    #날씨가 만약 비, 눈 등이 올 때 강수량, 적설량도 표시해야 됨. + 적운 등 어색한 단어를 적절한 단어로 변환해서 출력해야 됨.

    #날씨, 현재 기온 표시
    #print(f"날씨 : {today_weather_data['weather'][0]['main']}\n현재 기온 : {today_weather_data['main']['temp']}º")
    #최대 온도, 최소 온도 표시
    #print(f"최고 : {today_weather_data['main']['temp_max']} \n 최저 : {today_weather_data['main']['temp_max']}")
    #미세먼지, 습도 표시 
    #print(f"자외선 : {today_weather_data[]}")

# if __name__ == '__main__':
#     main()


app = Flask(__name__)
CORS(app)  # 개발용: 모든 출처 허용


@app.route("/api/data", methods=["GET"])
def get_data():
    data = final_data
    return jsonify(data)

# POST 예시 (클라이언트가 JSON을 보내면 처리)
@app.route("/api/echo", methods=["POST"])
def echo():
    payload = request.get_json(force=True)  # JSON 파싱
    payload["received"] = True
    return jsonify(payload), 201

if __name__ == "__main__":
    app.run(debug=True)








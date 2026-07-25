import requests
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import joblib
import pandas as pd

city_position={'lat':'','lon':''}
final_data=None

app = Flask(__name__)
CORS(app)


@app.route("/coords", methods=["POST"])
def coords():
    data = request.get_json()
    city_position['lat']=data.get("lat")
    city_position['lon']=data.get("lon")

    print("받은 좌표:", city_position)
    return jsonify({"status": "ok"})


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
def now_get_weather(city_position):

    #OpenWeather 데이터 호출값
    openweather_url = 'https://api.openweathermap.org/data/2.5/weather'
    openweather_api_key = '863577c3e6d70d7c15a60624a59fdf00'
    
    openweather_params = {
        'lat': city_position['lat'],
        'lon': city_position['lon'],
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
    



def now_get_dust(city_position) : 
    #한국환경공단 데이터 호출값(미세먼지, 오존)
    dust_url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
    dust_api_key = 'a2f8c0054fcb8adcd1da40e042d50a736e3eaceb7ad47fb611aca695e898820c'

    cloesst_gu=min(seoul_gu_coords.items(),
                    key=lambda x:abs(float(x[1]['lat'])-float(city_position['lat']))+
                    abs(float(x[1]['lon'])-float(city_position['lon'])))

    gu_name = cloesst_gu[0]

    dust_params = {
        'serviceKey' : dust_api_key,
        'returnType' : 'json',
        'numOfRows' : 1,
        'pageNo' : 1,
        'stationName' : gu_name,
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








def calculate_weather_score(data):
    score = 100
    
    weather_id = data.get('weather_id', 800) # 기본값 맑음(800)
    pm10 = float(data.get('pm10value',0))
    pm25 = float(data.get('pm25value',0))
    temp_max = data.get('temp_max', 0)
    temp_min = data.get('temp_min', 0)
    humidity = data.get('humidity', 0)
    wind_speed = data.get('wind_speed', 0)
    uv = int(data.get('o3grade',0))
    # 현재 API에는 자외선 정보가 없으므로 0으로 설정
    
    # 일교차 계산
    diff = abs(temp_max - temp_min)

    # 날씨 코드 
    code = weather_id // 100 
    
    if code == 2: score -= 50  # 뇌우
    if code == 3: score -= 30  # 이슬비
    if code == 5: score -= 40  # 비
    if code == 6: score -= 40  # 눈
    if code == 7: score -= 20  # 대기질(안개/황사)

    # --- [1] 미세먼지 ---
    if pm10 > 30:
        score -= (pm10 - 30) * 0.5
    if pm25 > 30:
        score -= (pm10 - 30) * 0.5
    
    # --- [2] 온도 ---
    if temp_max > 24: 
        score -= (temp_max - 24) * 2.7

    if 10 < temp_min < 18:
        score -= (18 - temp_min)
    elif temp_min <= 10:
        score -= (18 - temp_min) * 2.7
    
    # --- [3] 일교차 ---
    if diff > 7: 
        score -= (diff - 7) * 2.4
    
    # --- [4] 자외선 (데이터 있을 때만 동작, 현재는 데이터 없음) ---
    if 2 < uv < 6: 
        score -= (uv - 2) * 0.8
    elif uv >= 6: 
        score -= (uv - 6) * 2
    
    # --- [5] 습도 ---
    if humidity > 60:
        score -= (humidity - 60) * 1.5
    elif humidity < 40:
        score -= (40 - humidity) * 1.5

    # --- [6] 풍속 ---
    if wind_speed > 5:
        score -= (wind_speed - 5) * 1.5

    # 점수 범위 제한 (0~100)
    return max(0, min(100, round(score, 1)))




def get_outfit_recommendation(final_data):
    # 저장된 모델, 인코더 불러오기
    temp = final_data.get('temp',0)
    temp_min = final_data.get('temp_min',0)
    temp_max = final_data.get('temp_max',0)

    try:
        model = joblib.load('weather_outfit_model.pkl')
        encoders = joblib.load('outfit_encoders.pkl')
    except FileNotFoundError:
        return "모델 파일이 없음. 먼저 학습을 시켜야 됨."
    
    daily_range = abs(temp_max - temp_min)
    input_data = pd.DataFrame([[temp, temp_min, temp_max, daily_range]],  columns=['온도', '최저 온도', '최고 온도', '일교차'])
    
    #모델 예측 (숫자로 나옴)
    prediction = model.predict(input_data)

    #숫자를 다시 실제 옷 이름으로 변환
    target_cols = ['아우터', '상의', '하의', 'ACC']
    result = {}
    
    for i, col in enumerate(target_cols):
        # 예측값 prediction[0][i]를 그 컬럼의 인코더로 역변환
        result[col] = encoders[col].inverse_transform([prediction[0][i]])[0]

    return result


@app.route("/api/data", methods=["GET"])
def get_data():
    global final_data
    if not city_position['lat'] or not city_position['lon']:
        return jsonify({"error": "좌표가 설정되지 않았습니다."}), 400

    try:
        today_weather_data = now_get_weather(city_position)
        today_dust_data = now_get_dust(city_position)

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
    except:
        print("Error : NOT IN SEOUL_GU_COORDS")


    data = final_data
    return jsonify(data)

@app.route("/cloth/data", methods=["GET"])
def cloth_data():
    global cloth
    try:
        cloth=get_outfit_recommendation(final_data)
    except:
        print("Error: cloth error")
    return jsonify({"cloth" : cloth})

@app.route("/score/data", methods=["GET"])
def score_data():
    global score
    try:
        score=calculate_weather_score(final_data)
    except:
        print("Error: score error")
    return jsonify({"score" : score})


if __name__ == "__main__":
    app.run(debug=True)

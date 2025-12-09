async function loadData() {
    try {
    const res = await fetch('http://127.0.0.1:5000/api/data'); // 동일 컴퓨터에서 테스트
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const j = await res.json();

    function degreechanger(deg){
        const directions = [
            "북", "북북동", "북동", "동북동",
            "동", "동남동", "남동", "남남동",
            "남", "남남서", "남서", "서남서",
            "서", "서북서", "북서", "북북서"
        ];
        return directions[Math.round(deg/22.5)%16];
    }

    function pm10level(i){
        if(i<=30) return "좋음";
        if(i<=80) return "보통";
        if(i<=150) return "나쁨";
        return "매우나쁨";
    }
    
    function pm25level(i){
        if(i<=15) return "좋음";
        if(i<=35) return "보통";
        if(i<=75) return "나쁨";
        return "매우나쁨";
    }

    function o3level(i){
        const map = {
            "1":"좋음",
            "2":"보통",
            "3":"나쁨",
            "4":"매우나쁨"
        };
        return map[i] || "정보없음";
    }

    document.getElementById("main").innerText = "날씨상태: " + j.main;
    document.getElementById("temp").innerText = "현재기온: " + j.temp+"℃";
    document.getElementById("feels_like").innerText = "체감온도: " + j.feels_like+"℃";
    document.getElementById("temp_min").innerText = "최저기온: " + j.temp_min+"℃";
    document.getElementById("temp_max").innerText = "최대기온: " + j.temp_max+"℃";
    document.getElementById("humidity").innerText = "습도: " + j.humidity+"%";
    document.getElementById("wind_speed").innerText = "풍속: " + j.wind_speed+"m/s";

    document.getElementById("wind_degree").innerText = "풍향: " + degreechanger(j.wind_degree)+ " ("+j.wind_degree +"°)";
    document.getElementById("pm10value").innerText = "미세먼지: " + j.pm10value + "㎍/m³ ("+pm10level(j.pm10value)+")";
    document.getElementById("pm25value").innerText = "초미세먼지: " + j.pm25value + "㎍/m³ ("+pm25level(j.pm25value)+")";
    document.getElementById("o3grade").innerText = "오존: " + o3level(j.o3grade);

    // document.getElementById('msg').innerText = "메시지: " + j.msg;

    // const numbersUl = document.getElementById('numbers');
    // numbersUl.innerHTML = '';
    // j.numbers.forEach(n => {
    //     const li = document.createElement('li');
    //     li.innerText = n;
    //     numbersUl.appendChild(li);
    // });

    // const itemsUl = document.getElementById('items');
    // itemsUl.innerHTML = '';
    // j.items.forEach(it => {
    //     const li = document.createElement('li');
    //     li.innerText = `${it.id} — ${it.name}`;
    //     itemsUl.appendChild(li);
    // });

    } catch (err) {
        console.error(err);
        document.getElementById('msg').innerText = "로드 실패: " + err.message;
    }
}

// 페이지 로드 시 API 호출
loadData();
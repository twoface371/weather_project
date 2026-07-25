// function send(lat,lng) {

//     fetch("http://127.0.0.1:5000/send", {
//         method: "POST",
//         headers: {"Content-Type": "application/json"},
//         body: JSON.stringify({ lat: lat, lng: lng})
//     })
//     .then(res => res.json())
//     .then(data => console.log("서버 응답:", data))
//     .catch(err => console.error("에러:", err));
// }

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


    } catch (err) {
        console.error(err);
        document.getElementById('msg').innerText = "로드 실패: " + err.message;
    }
}

let isopen =false;
let map =null;
var marker= null;

async function loadscore() {
    try {
    const res = await fetch('http://127.0.0.1:5000/score/data'); // 동일 컴퓨터에서 테스트
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const score = await res.json();
    document.getElementById("score").innerText = "오늘의 날씨 점수: " + score.score;

    } catch (err) {
        console.error(err);
        document.getElementById('msg').innerText = "로드 실패: " + err.message;
    }
}

function scroll(){
    const target = document.getElementById("tns_title");
    target.scrollIntoView({
        behavior: "smooth",
        block: "start"
    })
}

async function loadcloth() {
    try {
    const res = await fetch('http://127.0.0.1:5000/cloth/data'); // 동일 컴퓨터에서 테스트
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const cloth = await res.json();
    document.getElementById("cloth").innerHTML = `
    <ul>
        <li>아우터: ${cloth.cloth.아우터}</li>
        <li>상의: ${cloth.cloth.상의}</li>
        <li>하의: ${cloth.cloth.하의}</li>
        <li>악세서리: ${cloth.cloth.ACC}</li>

    </ul>
    `;

    } catch (err) {
        console.error(err);
        document.getElementById('msg').innerText = "로드 실패: " + err.message;
    }
}

document.getElementById('togglebtn').addEventListener('click',function() {
    const wrapper = document.getElementById('mapwrapper');

    if(isopen){
        wrapper.style.display='none';
        this.innerText='지도 보기';
        isopen=false;
    }else{
        wrapper.style.display='block';
        this.innerText='지도 접기'
        isopen=true;
    
        if(!map){
            var mapContainer = document.getElementById('map'); 
                var mapOption = { 
                    center: new kakao.maps.LatLng(37.5665, 126.9780),
                    level: 3
                };

                map = new kakao.maps.Map(mapContainer, mapOption);

                kakao.maps.event.addListener(map, 'click', function(mouseEvent) {        
                    var latlng=mouseEvent.latLng;
                    const lat = mouseEvent.latLng.getLat();
                    const lng = mouseEvent.latLng.getLng();

                    if (marker !== null ) { 
                        marker.setMap(null)
                    };
                    marker = new kakao.maps.Marker({
                        position: latlng,
                        map: map
                    });
                    marker.setPosition(latlng);

                    document.getElementById('result').innerHTML = 
                        '위도: ' + lat + ', 경도: ' + lng;

                    fetch("http://127.0.0.1:5000/coords", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({ lat: lat, lon: lng })
                    })
                    .then(res => res.json())
                    .then(data => {
                        console.log("좌표 저장됨:", data);
                        loadData();
                        loadscore();
                        scroll();
                        loadcloth();
                    });
                   
                    setTimeout(() => map.relayout(),100);
                });
        }
    }
});

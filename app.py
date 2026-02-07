import streamlit as st
import requests
import pandas as pd
from streamlit_js_eval import get_geolocation

# 1. API 키 설정 (보안 규칙 준수)
API_KEY = st.secrets["WEATHER_API_KEY"]
BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

st.set_page_config(page_title="Korea Weather Hub", layout="wide")

# 4. 한글-영문 매칭 딕셔너리
KOREA_CITIES = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju", 
    "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "수원": "Suwon", "성남": "Seongnam", 
    "의정부": "Uijeongbu", "안양": "Anyang", "부천": "Bucheon", "광명": "Gwangmyeong", 
    "평택": "Pyeongtaek", "안산": "Ansan", "고양": "Goyang", "구리": "Guri", "남양주": "Namyangju", 
    "오산": "Osan", "시흥": "Siheung", "군포": "Gunpo", "의왕": "Uiwang", "하남": "Hanam", 
    "용인": "Yong인", "파주": "Paju", "이천": "Icheon", "안성": "Anseong", "김포": "Gimpo", 
    "화성": "Hwaseong", "양주": "Yangju", "포천": "Pocheon", "여주": "Yeoju", "아산": "Asan", 
    "천안": "Cheonan", "충주": "Chungju", "청주": "Cheongju", "전주": "Jeonju", "나주": "Naju", 
    "목포": "Mokpo", "여수": "Yeosu", "포항": "Pohang", "경주": "Gyeongju", "제주": "Jeju", "서귀포": "Seogwipo"
}

def get_weather_data(query):
    search_term = KOREA_CITIES.get(query, query)
    params = {"key": API_KEY, "q": search_term, "days": 7, "aqi": "no", "lang": "ko"}
    response = requests.get(BASE_URL, params=params)
    return response.json()

st.title("🌤️ 스마트 날씨 대시보드")

# 8. GPS 위치 정보
location = get_geolocation()

# --- 입력창 및 라벨 스타일 수정 ---
st.markdown(
    """
    <style>
    /* 1. 입력창 라벨(제목)을 검은색으로 설정 */
    .stTextInput label {
        color: #000000 !important;
        background-color: rgba(255, 255, 255, 0.8); /* 라벨 뒤에 살짝 배경을 넣어 잘 보이게 함 */
        padding: 2px 10px;
        border-radius: 5px;
        font-weight: bold !important;
    }
    
    /* 2. 입력창 내부 텍스트 및 안내 문구(Placeholder)를 검은색으로 설정 */
    div[data-baseweb="input"] input {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* 3. 안내 문구(Placeholder) 색상 강제 지정 */
    div[data-baseweb="input"] input::placeholder {
        color: #444444 !important;
        -webkit-text-fill-color: #444444 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

city_input = st.text_input("도시 이름을 한글로 입력하세요 (예: 아산, 서울, 제주)", "").strip()

query = city_input if city_input else None
if not query and location:
    lat, lon = location['coords']['latitude'], location['coords']['longitude']
    query = f"{lat},{lon}"

if query:
    data = get_weather_data(query)
    
    if "current" in data:
        curr = data['current']
        loc = data['location']
        cond = curr['condition']['text']
        temp = curr['temp_c']

        # 9. 날씨 기반 배경 이미지
        bg_url = "https://images.unsplash.com/photo-1534088568595-a066f7104211?q=80&w=2000"
        if "맑음" in cond: bg_url = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2000"
        elif "비" in cond: bg_url = "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?q=80&w=2000"
        elif "눈" in cond or "진눈깨비" in cond: bg_url = "https://images.unsplash.com/photo-1491002052546-bf38f186af56?q=80&w=2000"

        # 6. 전체 스타일링
        st.markdown(
            f"""
            <style>
            .stApp {{ 
                background-image: url("{bg_url}"); 
                background-size: cover; 
                background-attachment: fixed; 
            }}
            .glass {{ 
                background: rgba(0, 0, 0, 0.75); 
                padding: 30px; 
                border-radius: 20px; 
                border: 1px solid rgba(255,255,255,0.2);
            }}
            /* 결과창의 모든 글자는 흰색 유지 */
            .glass h1, .glass h2, .glass h3, .glass p, .glass span, 
            [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
                color: #FFFFFF !important;
                text-shadow: 2px 2px 8px rgba(0,0,0,1);
            }}
            </style>
            """, unsafe_allow_html=True
        )

        with st.container():
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.header(f"📍 {loc['name']} ({loc['country']})")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("현재 온도", f"{temp}°C")
            c2.metric("날씨 상태", cond)
            c3.metric("습도", f"{curr['humidity']}%")
            c4.metric("바람 세기", f"{curr['wind_kph']} km/h")

            if temp >= 30: st.error("너무 더워요! 🥵")
            st.markdown("---")
            
            # 10. 막대 그래프
            f_days = data['forecast']['forecastday']
            df = pd.DataFrame([{
                "날짜": d["date"][5:], 
                "최고기온": d["day"]["maxtemp_c"],
                "최저기온": d["day"]["mintemp_c"],
                "강수확률(%)": d["day"]["daily_chance_of_rain"]
            } for d in f_days]).set_index("날짜")

            st.subheader("🌡️ 7일 최고/최저 기온 (°C)")
            st.bar_chart(df[["최고기온", "최저기온"]])
            st.subheader("☔ 날짜별 강수 확률 (%)")
            st.bar_chart(df["강수확률(%)"])
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("지역을 찾을 수 없습니다.")
else:
    st.info("도시 이름을 입력하거나 GPS를 허용해 주세요.")
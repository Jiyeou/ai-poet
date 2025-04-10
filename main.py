import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests

# 환경변수 불러오기 (.env 또는 Streamlit Cloud Secrets)
load_dotenv()

# Upstash API 정보 확인 (디버깅용)
UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

st.write("Redis URL:", UPSTASH_REDIS_URL)
st.write("Redis Token (앞 10자리):", UPSTASH_REDIS_TOKEN[:10] + "..." if UPSTASH_REDIS_TOKEN else "❌ 없음")

# GPT 모델 초기화
chat_model = ChatOpenAI()

# Streamlit UI
st.title("감정 기반 거절 챗봇")

# 입력
target = st.selectbox("거절 대상", ["직장 상사", "친구", "가족", "모르는 사람"])
situation = st.text_input("상황 설명을 입력해주세요 (예: 회식 참석 요청 등)")
tone = st.radio("말투 선택", ["공손하게", "단호하게", "유쾌하게", "감성적으로"])

# 프롬프트 구성
prompt_template = PromptTemplate(
    input_variables=["tone", "target", "situation"],
    template=(
        "You are an expert at writing {tone} rejection messages to a {target} in the context of {situation}.\n"
        "Generate a brief and empathetic response that sounds natural."
    )
)

chain = LLMChain(llm=chat_model, prompt=prompt_template)

# 거절 메시지 생성
if st.button("거절 메시지 생성하기"):
    with st.spinner("AI가 메시지를 작성 중입니다..."):
        result = chain.run(tone=tone, target=target, situation=situation)
        st.success("생성된 메시지:")
        st.info(result)

        # Upstash에 저장 (디버깅 코드 포함)
        if UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN:
            save_url = f"{UPSTASH_REDIS_URL}/rpush/user_c_history/{result}"
            response = requests.post(
                save_url,
                headers={"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
            )
            st.write("저장 응답 코드:", response.status_code)
            st.write("저장 응답 내용:", response.text)
        else:
            st.warning("Upstash URL 또는 토큰이 없습니다.")

# 최근 메시지 보기
if st.button("최근 거절 메시지 보기"):
    if UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN:
        fetch_url = f"{UPSTASH_REDIS_URL}/lrange/user_c_history/0/4"
        response = requests.get(
            fetch_url,
            headers={"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
        )

        st.write("불러온 응답 코드:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            st.write("불러온 응답 원본:", data)  # JSON 전체 보기
            history = data.get("result", [])
            if history:
                st.subheader("최근 메시지들")
                for msg in history:
                    st.code(msg)
            else:
                st.info("최근 메시지가 없습니다.")
        else:
            st.error("메시지를 불러오는 데 실패했습니다.")
    else:
        st.warning("Upstash URL 또는 토큰이 없습니다.")

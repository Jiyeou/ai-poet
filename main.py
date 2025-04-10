import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests
import json

# 환경변수 로드
load_dotenv()

# GPT 모델 초기화
chat_model = ChatOpenAI()

# Streamlit UI 구성
st.title("🧠 감정 기반 거절 챗봇")

# 입력 받기
target = st.selectbox("거절 대상", ["직장 상사", "친구", "가족", "모르는 사람"])
situation = st.text_input("상황 설명을 입력해주세요 (예: 회식 참석 요청 등)")
tone = st.radio("말투 선택", ["공손하게", "단호하게", "유쾌하게", "감성적으로"])

# Upstash 정보 (Streamlit Secrets에 저장 권장)
UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

# 프롬프트 템플릿
prompt_template = PromptTemplate(
    input_variables=["tone", "target", "situation"],
    template=(
        "You are an expert at writing {tone} rejection messages to a {target} in the context of {situation}.\n"
        "Generate a brief and empathetic response that sounds natural."
    )
)
chain = LLMChain(llm=chat_model, prompt=prompt_template)

# 버튼 클릭 시 메시지 생성
if st.button("거절 메시지 생성하기"):
    with st.spinner("AI가 메시지를 작성 중입니다..."):
        result = chain.run(tone=tone, target=target, situation=situation)
        st.success("💬 생성된 메시지:")
        st.info(result)

        # 메시지 Upstash에 저장
        if UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN:
            requests.post(
                f"{UPSTASH_REDIS_URL}/rpush/user_c_history",
                headers={"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"},
                data=json.dumps(result)
            )

# 최근 응답 불러오기
if st.button("최근 거절 메시지 보기"):
    if UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN:
        resp = requests.get(
            f"{UPSTASH_REDIS_URL}/lrange/user_c_history/0/4",
            headers={"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
        )
        history = resp.json()
        st.subheader("🕘 최근 메시지들")
        for msg in history:
            st.code(msg)

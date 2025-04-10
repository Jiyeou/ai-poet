import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests

# 🌱 환경변수 불러오기 (.env or Streamlit Cloud Secrets)
load_dotenv()

# 🔑 API 키 가져오기
UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")

# 🧠 GPT 모델 초기화
chat_model = ChatOpenAI()

# 🖥️ Streamlit UI 시작
st.title("🧠 감정 기반 거절 챗봇")

# 사용자 입력 받기
target = st.selectbox("거절 대상", ["직장 상사", "친구", "가족", "모르는 사람"])
situation = st.text_input("상황 설명을 입력해주세요 (예: 회식 참석 요청 등)")
tone = st.radio("말투 선택", ["공손하게", "단호하게", "유쾌하게", "감성적으로"])

# ✏️ 프롬프트 템플릿 정의
prompt_template = PromptTemplate(
    input_variables=["tone", "target", "situation"],
    template=(
        "You are an expert at writing {tone} rejection messages to a {target} in the context of {situation}.\n"
        "Generate a brief and empathetic response that sounds natural."
    )
)

# 🧠 LangChain 체인 생성
chain = LLMChain(llm=chat_model, prompt=prompt_template)

# ✅ 메시지 생성 버튼
if st.button("거절 메시지 생성하기"):
    with st.spinner("AI가 메시지를 작성 중입니다..."):
        result = chain.run(tone=tone, target=target, situation=situation)
        st.success("💬 생성된 메시지:")
        st.info(result)

        # 🔐 Upstash에 메시지 저장
        if UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN:
            save_url = f"{UPSTASH_REDIS_URL}/rpush/user_c_history/{result}"
            response = requests.post(
                save_url,
                headers={"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
            )
            if response.status_code != 200:
                st.warning("⚠️ 메시지 저장 실패! 다시 시도해 주세요.")

# 📜 최근 거절 메시지 보기
if st.button("최근 거절 메시지 보기"):
    if UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN:
        fetch_url = f"{UPSTASH_REDIS_URL}/lrange/user_c_history/0/4"
        response = requests.get(
            fetch_url,
            headers={"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"}
        )
        if response.status_code == 200:
            history = response.json().get("result", [])
            if history:
                st.subheader("🕘 최근 메시지들")
                for msg in history:
                    st.code(msg)
            else:
                st.info("최근 메시지가 없습니다.")
        else:
            st.error("❌ 메시지를 불러오는 데 실패했습니다.")

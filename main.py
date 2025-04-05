from dotenv import load_dotenv
load_dotenv() #키를 괄호 안에 직접 넣어도 되지만 노출될 위험 존재재
import streamlit as st
from langchain.chat_models import ChatOpenAI

# from langchain.llms import OpenAI
# llm = OpenAI()
# result=llm.predict("hi") #OpenAI은 위에 문장을 자동완성 해주는 기능능
# print(result)


chat_model = ChatOpenAI()

st.title("인공지능 시인")

content=st.text_input("시의 주제를 제시해주세요")

if st.button("시 작성 요청하기"):
    result=chat_model.predict(content + "에 대한 시를 써줘")
    st.write(result)


# st.write("시의 주제는", title)


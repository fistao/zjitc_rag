import streamlit as st
import requests

# Streamlit界面
st.title("💻 软件教学问答系统")
st.caption("低成本版 - 基于DeepSeek-Coder和Neo4j")

question = st.text_input("输入编程相关问题：", placeholder="例如：什么是MVC模式？")

if st.button("获取答案"):
    if question:
        with st.spinner("正在思考中..."):
            response = requests.post(
                "http://localhost:5000/ask", 
                json={"question": question}
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success("### 回答")
                st.write(result['answer'])
                
                # 显示知识图谱关联
                st.info("### 相关知识点")
                st.write("- 面向对象\n- 设计模式\n- Spring框架")
            else:
                st.error("服务暂不可用，请稍后再试")
    else:
        st.warning("请输入问题")
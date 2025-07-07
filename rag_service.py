import faiss
import torch
import os
import numpy as np
from text2vec import SentenceModel
from transformers import AutoTokenizer, pipeline
from neo4j import GraphDatabase

# 配置Neo4j连接
NEO4J_URI = "neo4j+s://df0b5442.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "JQmCHP8wN98l_m5GR-owlf3-FXELcIptwH2SWWhyIoI"

# 1. 向量模型和索引
# 在加载模型前设置环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # 完全离线模式
os.environ["HF_DATASETS_OFFLINE"] = "1"  # 数据集离线
os.environ["HF_HUB_OFFLINE"] = "1"  # 强制使用本地缓存
model = SentenceModel('shibing624/text2vec-base-chinese')
index = faiss.IndexFlatL2(768)  # 向量维度

# 2. 生成模型 (DeepSeek-Coder 1.3B)
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct")
generator = pipeline(
    "text-generation",
    model="deepseek-ai/deepseek-coder-1.3b-instruct",
    device_map="auto",
    torch_dtype=torch.float16
)

# 3. 检索函数
def retrieve(question, top_k=3):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    query_vec = model.encode([question])[0].tolist()  # 转换为Python列表
    
    cypher_query = """
    WITH $vec AS query_vec
    MATCH (c:Chunk)
    WITH c, gds.similarity.cosine(query_vec, c.embedding) AS similarity
    ORDER BY similarity DESC
    LIMIT $top_k
    RETURN c.text AS text
    """
    
    with driver.session() as session:
        result = session.run(
            cypher_query,
            vec=query_vec,
            top_k=top_k
        )
        chunks = [record["text"] for record in result]
    
    driver.close()
    return chunks

# 4. 生成回答
def generate_answer(question):
    # 检索上下文
    context = "\n".join(retrieve(question))
    
    # 构建Prompt
    prompt = f"""你是一个软件工程助教，请根据上下文回答问题：
    
[上下文]
{context}

[问题]
{question}

[回答]
"""
    # 生成回答
    result = generator(
        prompt,
        max_new_tokens=256,
        temperature=0.3,
        do_sample=True
    )
    return result[0]['generated_text'][len(prompt):]

# 5. 初始化数据
chunks = ["面向对象编程有三大特性：封装、继承、多态...", 
          "Spring Boot是一个Java开发框架..."]
chunk_vectors = model.encode(chunks)
index.add(np.array(chunk_vectors).astype('float32'))

# 测试
print(generate_answer("什么是面向对象编程？"))
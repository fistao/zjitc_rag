import faiss
import numpy as np
from text2vec import SentenceModel
from transformers import AutoTokenizer, pipeline

# 1. 向量模型和索引
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
    # 文本向量化
    query_vec = model.encode([question])[0]
    
    # FAISS搜索
    _, indices = index.search(np.array([query_vec]).astype('float32'), top_k)
    
    # 返回相关文本块
    return [chunks[i] for i in indices[0]]

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
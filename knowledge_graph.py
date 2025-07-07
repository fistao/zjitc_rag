from neo4j import GraphDatabase
import numpy as np
from text2vec import SentenceModel

# Neo4j Aura免费版连接
URI  = "neo4j+s://df0b5442.databases.neo4j.io"
USER  = "neo4j"
PASSWORD  = "JQmCHP8wN98l_m5GR-owlf3-FXELcIptwH2SWWhyIoI"

# 文本块数据
CHUNKS = [
    "面向对象编程有三大特性：封装、继承、多态。封装隐藏实现细节，继承实现代码复用，多态允许不同对象响应相同消息。",
    "Spring Boot是一个Java开发框架，通过自动配置简化了Spring应用的初始搭建和开发过程。",
    "设计模式中的MVC模式将应用分为模型(Model)、视图(View)和控制器(Controller)三层。",
    "数据库事务应满足ACID特性：原子性(Atomicity)、一致性(Consistency)、隔离性(Isolation)、持久性(Durability)。"
]

# 概念和关系
CONCEPTS = [
    ("面向对象", "理论"), ("继承", "特性"), 
    ("Spring Boot", "框架"), ("MVC", "模式"),
    ("事务", "概念"), ("ACID", "特性")
]

RELATIONS = [
    ("面向对象", "HAS_FEATURE", "继承"),
    ("Spring Boot", "IMPLEMENTS", "MVC"),
    ("事务", "HAS_PROPERTY", "ACID")
]

def create_chunk(tx, text, embedding):
    tx.run(
        "CREATE (c:Chunk {text: $text, embedding: $embedding})",
        text=text, embedding=embedding
    )

def create_concept(tx, name, type):
    tx.run(
        "MERGE (c:Concept {name: $name, type: $type})",
        name=name, type=type
    )

def create_relation(tx, source, rel, target):
    tx.run(
        "MATCH (a:Concept {name: $source}), (b:Concept {name: $target}) "
        "MERGE (a)-[:`"+rel+"`]->(b)",
        source=source, target=target
    )

def build_graph():
    # 加载文本嵌入模型
    model = SentenceModel('shibing624/text2vec-base-chinese')
    chunk_vectors = model.encode(CHUNKS)
    
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    with driver.session() as session:
        # 创建文本块节点（带向量）
        for text, vec in zip(CHUNKS, chunk_vectors):
            session.execute_write(
                create_chunk, 
                text=text, 
                embedding=vec.tolist()  # 转换为Python列表
            )
        
        # 创建概念节点
        for name, type in CONCEPTS:
            session.execute_write(create_concept, name, type)
        
        # 创建概念关系
        for src, rel, tgt in RELATIONS:
            session.execute_write(create_relation, src, rel, tgt)
    
    driver.close()
    print("知识图谱构建完成！")

if __name__ == "__main__":
    build_graph()
    # 添加向量索引（只需运行一次）
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
        FOR (c:Chunk) ON (c.embedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: 768,
            `vector.similarity_function`: 'cosine'
        }}
        """)
    driver.close()
    print("向量索引创建完成！")
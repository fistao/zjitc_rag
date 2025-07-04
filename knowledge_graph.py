from neo4j import GraphDatabase

# Neo4j Aura免费版连接
uri = "neo4j+s://df0b5442.databases.neo4j.io"
user = "neo4j"
password = "JQmCHP8wN98l_m5GR-owlf3-FXELcIptwH2SWWhyIoI"

driver = GraphDatabase.driver(uri, auth=(user, password))

def create_concept(tx, name, type):
    tx.run("MERGE (c:Concept {name: $name, type: $type})", name=name, type=type)

def create_relation(tx, source, rel, target):
    tx.run(
        "MATCH (a:Concept {name: $source}), (b:Concept {name: $target}) "
        "MERGE (a)-[:`"+rel+"`]->(b)",
        source=source, target=target
    )

# 从处理后的数据构建图谱
def build_graph():
    # 添加核心概念
    concepts = [
        ("面向对象", "理论"), ("继承", "特性"), 
        ("Spring Boot", "框架"), ("MVC", "模式")
    ]
    
    relations = [
        ("面向对象", "HAS_FEATURE", "继承"),
        ("Spring Boot", "IMPLEMENTS", "MVC")
    ]
    
    with driver.session() as session:
        # 创建节点
        for name, type in concepts:
            session.execute_write(create_concept, name, type)
        
        # 创建关系
        for src, rel, tgt in relations:
            session.execute_write(create_relation, src, rel, tgt)
    
    print("知识图谱构建完成！")

if __name__ == "__main__":
    build_graph()
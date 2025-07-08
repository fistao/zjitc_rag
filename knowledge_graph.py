import os
import re
from neo4j import GraphDatabase
from text2vec import SentenceModel

# 目录配置
CLEANED_DATA_DIR = "data/cleaned" # 处理后文本目录

class KnowledgeGraph:
    """自动构建知识图谱"""
    
    def __init__(self):
        # Neo4j 连接配置
        self.uri = "neo4j+s://df0b5442.databases.neo4j.io"
        self.user = "neo4j"
        self.password = "JQmCHP8wN98l_m5GR-owlf3-FXELcIptwH2SWWhyIoI"
        
        # 文本嵌入模型
        self.model = SentenceModel('shibing624/text2vec-base-chinese')
    
    def extract_key_terms(self, text):
        """从文本中提取关键术语"""
        # 提取大写词组（技术术语）
        terms = set()
        
        # 匹配技术术语（如"Artificial Intelligence"）
        for match in re.finditer(r'([A-Z][a-z]+){2,}', text):
            terms.add(match.group(0))
        
        # 匹配缩写（如"AI"）
        for match in re.finditer(r'\b[A-Z]{2,}\b', text):
            terms.add(match.group(0))
        
        return list(terms)
    
    def build_relations(self, terms):
        """构建术语之间的关系"""
        relations = []
        
        # 简单规则：相邻术语建立关系
        for i in range(len(terms) - 1):
            relations.append((terms[i], "RELATED_TO", terms[i+1]))
        
        return relations
    
    def create_graph(self):
        """创建知识图谱"""
        # 检查是否有清洗后的文本
        if not os.path.exists(CLEANED_DATA_DIR) or not os.listdir(CLEANED_DATA_DIR):
            print(f"没有找到清洗后的文本文件，请先运行 data_processing.py 并确保 {CLEANED_DATA_DIR} 中有文件")
            return
        
        # 连接到Neo4j
        driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        
        processed_files = 0
        with driver.session() as session:
            # 处理所有清洗后的文本文件
            for file in os.listdir(CLEANED_DATA_DIR):
                if file.endswith('.txt'):
                    file_path = os.path.join(CLEANED_DATA_DIR, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        
                        # 跳过空文件
                        if not text.strip():
                            print(f"跳过空文件: {file}")
                            continue
                        
                        print(f"处理文本文件: {file}")
                        
                        # 生成文本向量
                        embedding = self.model.encode([text])[0].tolist()
                        
                        # 提取关键术语
                        key_terms = self.extract_key_terms(text)
                        
                        if not key_terms:
                            print(f"未在 {file} 中找到关键术语")
                            continue
                            
                        print(f"提取到 {len(key_terms)} 个关键术语")
                        
                        # 构建关系
                        relations = self.build_relations(key_terms)
                        
                        # 创建文本块节点
                        session.execute_write(
                            self.create_text_chunk,
                            text=text[:500],  # 存储前500字符
                            embedding=embedding,
                            source=file
                        )
                        
                        # 创建术语节点
                        for term in key_terms:
                            session.execute_write(
                                self.create_concept,
                                name=term,
                                type="技术术语"
                            )
                            
                            # 链接文本块和术语
                            session.execute_write(
                                self.link_chunk_to_concept,
                                source_file=file,
                                concept_name=term
                            )
                        
                        # 创建术语间关系
                        for source, rel_type, target in relations:
                            session.execute_write(
                                self.create_relation,
                                source=source,
                                rel_type=rel_type,
                                target=target
                            )
                        
                        processed_files += 1
        
        driver.close()
        print(f"知识图谱构建完成! 处理了 {processed_files} 个文件")
    
    # Neo4j 操作辅助方法
    @staticmethod
    def create_text_chunk(tx, text, embedding, source):
        tx.run(
            "CREATE (c:TextChunk {text: $text, embedding: $embedding, source: $source})",
            text=text, embedding=embedding, source=source
        )
    
    @staticmethod
    def create_concept(tx, name, type):
        tx.run(
            "MERGE (c:Concept {name: $name}) "
            "ON CREATE SET c.type = $type",
            name=name, type=type
        )
    
    @staticmethod
    def link_chunk_to_concept(tx, source_file, concept_name):
        tx.run(
            "MATCH (chunk:TextChunk {source: $source_file}), (concept:Concept {name: $concept_name}) "
            "MERGE (chunk)-[:MENTIONS]->(concept)",
            source_file=source_file, concept_name=concept_name
        )
    
    @staticmethod
    def create_relation(tx, source, rel_type, target):
        tx.run(
            "MATCH (a:Concept {name: $source}), (b:Concept {name: $target}) "
            "MERGE (a)-[:`"+rel_type+"`]->(b)",
            source=source, target=target
        )
    
    def create_vector_index(self):
        """创建向量索引"""
        driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        with driver.session() as session:
            session.run("""
            CREATE VECTOR INDEX text_embeddings IF NOT EXISTS
            FOR (c:TextChunk) ON (c.embedding)
            OPTIONS {indexConfig: {
                `vector.dimensions`: 768,
                `vector.similarity_function`: 'cosine'
            }}
            """)
        driver.close()
        print("向量索引创建完成！")

if __name__ == "__main__":
    # 构建知识图谱
    print("="*50)
    print("知识图谱构建开始")
    print("="*50)
    kg = KnowledgeGraph()
    kg.create_graph()
    kg.create_vector_index()
    print("\n" + "="*50)
    print("知识图谱构建完成!")
    print("="*50)
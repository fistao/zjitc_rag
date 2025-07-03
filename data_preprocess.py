import os
import re
from bs4 import BeautifulSoup
from tree_sitter import Parser, Language

# 文本清洗
def clean_text(text):
    # 去HTML标签
    text = BeautifulSoup(text, 'html.parser').get_text()
    # 去特殊字符
    text = re.sub(r'[^\w\s.,;:!?()\[\]{}\'"]', '', text)
    return text

# 代码解析 (Java示例)
def parse_java(code):
    # 加载Java语法
    JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
    parser = Parser()
    parser.set_language(JAVA_LANGUAGE)
    
    tree = parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node
    
    # 提取类和方法
    entities = []
    for node in root_node.children:
        if node.type == 'class_declaration':
            class_name = node.child_by_field_name('name').text.decode()
            entities.append(f"Class: {class_name}")
            
            # 提取方法
            for child in node.children:
                if child.type == 'method_declaration':
                    method_name = child.child_by_field_name('name').text.decode()
                    entities.append(f"Method: {class_name}.{method_name}")
    return entities

# 主处理流程
def process_data():
    # 遍历数据目录
    for file in os.listdir('raw_data'):
        if file.endswith('.txt'):
            with open(f"raw_data/{file}", 'r') as f:
                text = clean_text(f.read())
                # 保存清洗后文本
                with open(f"cleaned/{file}", 'w') as out:
                    out.write(text)
                    
        elif file.endswith('.java'):
            with open(f"raw_data/{file}", 'r') as f:
                code = f.read()
                entities = parse_java(code)
                # 保存代码实体
                with open(f"entities/{file}.ent", 'w') as out:
                    out.write("\n".join(entities))
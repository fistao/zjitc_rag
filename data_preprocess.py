import os
import re
import fitz  # PyMuPDF
from bs4 import BeautifulSoup

# 目录配置
RAW_DATA_DIR = "data/raw"         # 原始PDF目录
CLEANED_DATA_DIR = "data/cleaned" # 处理后文本目录

def ensure_directories():
    """确保必要的目录存在"""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(CLEANED_DATA_DIR, exist_ok=True)
    print(f"确保目录存在: {RAW_DATA_DIR}, {CLEANED_DATA_DIR}")

def process_pdfs():
    """处理data/raw目录中的所有PDF文件"""
    ensure_directories()
    
    # 获取所有PDF文件
    pdf_files = [f for f in os.listdir(RAW_DATA_DIR) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"未找到PDF文件，请将PDF文件放在 {RAW_DATA_DIR} 目录中")
        return
    
    print(f"找到 {len(pdf_files)} 个PDF文件待处理")
    
    processed_count = 0
    for pdf_file in pdf_files:
        try:
            print(f"\n处理文件: {pdf_file}")
            input_path = os.path.join(RAW_DATA_DIR, pdf_file)
            text = ""
            
            # 提取PDF文本
            with fitz.open(input_path) as doc:
                for page in doc:
                    text += page.get_text()
            
            # 文本清洗
            text = BeautifulSoup(text, 'html.parser').get_text()
            text = re.sub(r'[^\w\s.,;:!?()\[\]{}\'"]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # 保存清洗后的文本
            output_file = f"{pdf_file.replace('.pdf', '.txt')}"
            output_path = os.path.join(CLEANED_DATA_DIR, output_file)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"已保存清洗文本: {output_path}")
            processed_count += 1
        
        except Exception as e:
            print(f"处理 {pdf_file} 时出错: {str(e)}")
    
    print(f"\n处理完成! 共处理 {processed_count}/{len(pdf_files)} 个文件")
    return processed_count > 0

if __name__ == "__main__":
    # 处理PDF文件
    print("="*50)
    print("PDF文件处理开始")
    print("="*50)
    process_pdfs()
    print("\n" + "="*50)
    print("PDF处理完成!")
    print("="*50)
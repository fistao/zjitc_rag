#!/bin/bash

# 1. 安装依赖
pip install -r requirements.txt

# 2. 下载模型（首次运行）
#text2vec和DeepSeek-Coder会自动下载

# 3. 启动后端
nohup python app.py > backend.log &

# 4. 启动前端
python -m streamlit run ui.py --server.port 8501
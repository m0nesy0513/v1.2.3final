# 族谱勘查 v1.2.3 Final

## 本地运行
1. 创建 Python 3.12 虚拟环境
2. 安装依赖：
   `pip install -r requirements.txt`
3. 复制 `.streamlit/secrets.toml.example` 为 `.streamlit/secrets.toml`
4. 填入 `DEEPSEEK_API_KEY` 和 `TAVILY_API_KEY`
5. 把审查案例 DOCX 放入 `knowledge_base/`
6. 运行：
   `streamlit run app.py`

## 部署到 Streamlit Cloud
1. 上传项目到 GitHub（不要上传 `.streamlit/secrets.toml` 和 `data/`）
2. 在 Streamlit Cloud 选择仓库和 `app.py`
3. 在 App Settings → Secrets 中配置：
   - `DEEPSEEK_API_KEY`
   - `TAVILY_API_KEY`

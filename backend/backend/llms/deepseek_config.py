from llama_index.core import  Settings
from llama_index.llms.deepseek import DeepSeek
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import PropertyGraphIndex
import os
from pydantic import Field, SecretStr  # 导入 Pydantic 字段类型
import requests
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata  # 新增 LLMMetadata

# you can also set DEEPSEEK_API_KEY in your environment variables
# llm = DeepSeek(model="deepseek-reasoner", api_key="sk-389d05c788654c9f8ddbfd686bdc8d5a")
# llm = DeepSeek(model="deepseek-chat", api_key="sk-389d05c788654c9f8ddbfd686bdc8d5a")
# 配置自定义 HTTP 后端（重试 + 超时调整）


from llama_index.llms.openai_like import OpenAILike

# llm = OpenAILike(
#     model="DeepSeek-R1",
#     api_base="https://llmapi.tongji.edu.cn/v1",
#     api_key="HCxnZCW9FqdSXsyMDc186aF67b234230Ab06B0Ee89EbD246",
#     temperature=0.3,
#     context_window=128000,
#     is_chat_model=True,
# )




# index = PropertyGraphIndex.from_existing(
#     property_graph_store=pg_store,
#     llm=Settings.llm,
#     embed_model=Settings.embed_model,
#     embed_kg_nodes=True,
#     verbose=True,
#     show_progress=True,
# )
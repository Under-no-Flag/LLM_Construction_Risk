from backend.llms.deepseek_config import (Settings)
from backend.llms.utils import llm_str2json
from llama_index.core import PropertyGraphIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.deepseek import DeepSeek

def query_kg_for_suggestion(risk_description: str) -> str:
    """
    调用 DeepSeek LLM 返回一段中文分析文本
    """
    # llm = DeepSeek(model="deepseek-reasoner", api_key="sk-389d05c788654c9f8ddbfd686bdc8d5a")
    llm = DeepSeek(model="deepseek-chat", api_key="sk-389d05c788654c9f8ddbfd686bdc8d5a")
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-zh-v1.5",
        cache_folder="./",
        device="cuda:0",
    )
    print("embed_model加载成功","BAAI/bge-small-zh-v1.5")

    pg_store = Neo4jPropertyGraphStore(
    username="neo4j",
    password="Neo4j@0407",
    url="bolt://127.0.0.1:7687",
    database='vectorKG',
)
    print("图数据库连接成功")
    query_index = PropertyGraphIndex.from_existing(
        property_graph_store=pg_store,
        llm=Settings.llm,
        embed_model=Settings.embed_model,
        verbose=True,
        show_progress=True,
    )
    query_engine = query_index.as_query_engine(
        include_text=True,
    )
    print("query_engine", risk_description)
    suggestion_prompt = f"根据风险隐患描述：{risk_description}和相关安全法规、事故报告、建筑施工标准和条例，提出针对风险隐患的治理整改意见。请用中文回答 返回格式json"+ "{\"suggestions\": [\"整改意见1\", \"整改意见2\"]}。请注意，返回的json格式必须是有效的，否则将无法解析。"

    response = query_engine.query(suggestion_prompt)

#     response="""
# ```json
# {
#   "suggestions": [
#     "立即在挖掘机周围设置明显的警示标志和围栏，防止人员误入施工区域",
#     "对施工现场地面进行平整处理，消除绊倒风险",
#     "设置明显的安全通道标识，确保紧急疏散路径清晰可见"
#   ]
# }
# ```
# """

    suggestions=llm_str2json(str(response))

    return suggestions



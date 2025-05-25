# kg_service.py
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import PropertyGraphIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import Settings

class KnowledgeGraphService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        import os
        print("当前工作目录:", os.getcwd())
        pass

    def query_graph(self, query_text):

        """应用启动时初始化"""
        try:
            # 初始化嵌入模型
            self.embed_model = HuggingFaceEmbedding(
                model_name="BAAI/bge-small-zh-v1.5",
                cache_folder="./"
            )
            Settings.embed_model = self.embed_model

            # 初始化LLM
            self.llm = OpenAILike(
                model="DeepSeek-R1",
                api_base="https://llmapi.tongji.edu.cn/v1",
                api_key="HCxnZCW9FqdSXsyMDc186aF67b234230Ab06B0Ee89EbD246",
                temperature=0.3,
                context_window=128000,
                is_chat_model=True,
            )
            Settings.llm = self.llm

            # Neo4j连接
            self.graph_store = Neo4jPropertyGraphStore(
                username="neo4j",
                password="Neo4j@0407",
                url="bolt://localhost:7687",
                database="vectorkg",
            )

            # 创建索引
            self.index = PropertyGraphIndex.from_existing(
                property_graph_store=self.graph_store,
                llm=self.llm,
                embed_model=self.embed_model
            )
        except Exception as e:
            raise RuntimeError(f"知识图谱服务初始化失败: {str(e)}")

        """执行图谱查询"""
        try:
            print("图查询指令",query_text)
            nodes = self.index.as_retriever(include_text=False).retrieve(query_text)
            return self._process_nodes(nodes)
        except Exception as e:
            print(f"图谱查询异常: {str(e)}")
            return []

    def _process_nodes(self, nodes):
        """处理节点数据"""
        nodes_set = set()
        edges = []

        for node in nodes:
            if "->" in node.text:
                parts = node.text.split("->")
                if len(parts) == 3:
                    source = parts[0].strip()
                    edge = parts[1].strip()
                    target = parts[2].strip()

                    nodes_set.add(source)
                    nodes_set.add(target)
                    edges.append({
                        'data': {
                            'source': source,
                            'target': target,
                            'label': edge
                        }
                    })

        graph_nodes = [{
            'data': {
                'id': node,
                'label': node
            }
        } for node in nodes_set]

        return graph_nodes + edges

# 单例实例
kg_service = KnowledgeGraphService()
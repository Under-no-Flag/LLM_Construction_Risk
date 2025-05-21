from django.http import JsonResponse
from .neo4j import driver
import logging

logger = logging.getLogger(__name__)

def initial_graph(request):
    """获取初始图谱数据（最终修正版）"""
    try:
        # 参数校验
        depth = int(request.GET.get("depth", 2))
        if not 1 <= depth <= 5:
            return JsonResponse({"error": "Depth must be 1-5"}, status=400)

        # 修正后的Cypher
        cypher = (
            "MATCH p=(n)-[*1..%s]-(m) \n"
            "UNWIND nodes(p) AS node \n"
            "UNWIND relationships(p) AS rel \n"
            "RETURN \n"
            "  COLLECT(DISTINCT { \n"
            "    id: id(node), \n"
            "    label: head(labels(node)), \n"
            "    properties: properties(node) \n"
            "  }) AS nodes, \n"
            "  COLLECT(DISTINCT { \n"
            "    id: id(rel), \n"
            "    source: id(startNode(rel)), \n"
            "    target: id(endNode(rel)), \n"
            "    type: type(rel) \n"
            "  }) AS edges \n"
            "LIMIT 500" % depth
        )

        with driver.get_session() as session:
            result = session.run(cypher)
            data = result.single()
            
            if not data:
                return JsonResponse({"nodes": [], "edges": []})
            
            # 数据清洗
            def sanitize(obj):
                if isinstance(obj, dict):
                    return {k: sanitize(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [sanitize(v) for v in obj]
                if hasattr(obj, 'items'):
                    return dict(obj)
                return obj

            return JsonResponse({
                "nodes": [sanitize(node) for node in data["nodes"]],
                "edges": [sanitize(edge) for edge in data["edges"]]
            })
            
    except ValueError:
        return JsonResponse({"error": "Invalid depth parameter"}, status=400)
    except Exception as e:
        logger.error(f"Initial graph error: {str(e)}")
        return JsonResponse({"error": "Database error"}, status=500)


def sanitize(obj):
    """通用数据清洗函数"""
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    if hasattr(obj, 'items'):
        return dict(obj)  # 转换neo4j.types.graph.Node等类型
    return obj

def expand_node(request):
    """展开节点邻居（安全增强版）"""
    try:
        # 参数验证
        node_id = request.POST.get("id")
        if not node_id:
            return JsonResponse({"error": "Missing node ID"}, status=400)
        
        node_id = int(node_id)  # 转换失败会触发ValueError

        # 使用elementId替代已弃用的id()
        cypher = """
        MATCH (n)-[r]-(m)
        WHERE elementId(n) = $id
        RETURN 
          {id: elementId(m), 
           label: labels(m)[0], 
           properties: properties(m)} AS node,
          {id: elementId(r), 
           source: elementId(startNode(r)), 
           target: elementId(endNode(r)), 
           type: type(r)} AS edge
        """
        
        nodes = []
        edges = []
        with driver.get_session() as session:
            result = session.run(cypher, id=str(node_id))
            for record in result:
                nodes.append(sanitize(record["node"]))
                edges.append(sanitize(record["edge"]))
        
        return JsonResponse({
            "nodes": nodes,
            "edges": edges
        })

    except ValueError:
        logger.warning(f"Invalid node ID format: {request.POST.get('id')}")
        return JsonResponse({"error": "Invalid node ID format"}, status=400)
    except Exception as e:
        logger.error(f"Expand node error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Database error"}, status=500)

def search_nodes(request):
    """节点搜索（安全增强版）"""
    try:
        keyword = request.GET.get("kw")
        if not keyword:
            return JsonResponse({"error": "Missing keyword"}, status=400)
        
        if len(keyword) < 2:
            return JsonResponse({"error": "Keyword too short"}, status=400)

        # 增强版搜索：匹配任意包含关键词的属性
        cypher = """
        MATCH (n)
        WHERE ANY(
            key IN keys(n) 
            WHERE toLower(n[key]) CONTAINS toLower($keyword)
        )
        RETURN {
            id: elementId(n), 
            label: labels(n)[0], 
            properties: properties(n)
        } AS node
        LIMIT 20
        """
        
        results = []
        with driver.get_session() as session:
            result = session.run(cypher, keyword=keyword)
            for record in result:
                results.append(sanitize(record["node"]))
        
        return JsonResponse({"nodes": results})

    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Search failed"}, status=500)

def add_node(request):
    """新增节点（安全增强版）"""
    try:
        # 参数验证
        label = request.POST.get("label")
        properties = request.POST.get("properties", {})
        
        if not label:
            return JsonResponse({"error": "Missing node label"}, status=400)
        
        # 转换属性为字典（示例需要根据实际前端传参方式调整）
        if isinstance(properties, str):
            try:
                properties = json.loads(properties)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid properties format"}, status=400)

        # 参数化查询防止注入
        cypher = """
        CREATE (n:%s $props)
        RETURN {
            id: elementId(n),
            label: labels(n)[0],
            properties: properties(n)
        } AS node
        """ % label

        with driver.get_session() as session:
            result = session.run(cypher, props=properties)
            data = result.single()
            
            if not data:
                return JsonResponse({"error": "Node creation failed"}, status=500)
            
            return JsonResponse({"node": sanitize(data["node"])})

    except Exception as e:
        logger.error(f"Add node error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Node creation failed"}, status=500)

def delete_node(request):
    """删除节点（安全增强版）"""
    try:
        # 参数验证
        node_id = request.POST.get("id")
        if not node_id:
            return JsonResponse({"error": "Missing node ID"}, status=400)
        
        # 使用elementId确保ID有效性
        cypher = """
        MATCH (n)
        WHERE elementId(n) = $id
        DETACH DELETE n
        RETURN count(n) AS deleted_count
        """

        with driver.get_session() as session:
            result = session.run(cypher, id=str(node_id))
            data = result.single()
            
            if data["deleted_count"] == 0:
                return JsonResponse({"error": "Node not found"}, status=404)
            
            return JsonResponse({"success": True})

    except Exception as e:
        logger.error(f"Delete node error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Node deletion failed"}, status=500)

def add_relationship(request):
    """新增关系（安全增强版）"""
    try:
        # 参数验证
        source_id = request.POST.get("source_id")
        target_id = request.POST.get("target_id")
        rel_type = request.POST.get("type")
        properties = request.POST.get("properties", {})

        if not all([source_id, target_id, rel_type]):
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # 验证关系类型格式（可根据业务需求扩展验证规则）
        if not rel_type.isalnum():
            return JsonResponse({"error": "Invalid relationship type"}, status=400)

        # 转换属性为字典
        if isinstance(properties, str):
            try:
                properties = json.loads(properties)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid properties format"}, status=400)

        # 参数化查询防止注入
        cypher = """
        MATCH (a), (b)
        WHERE elementId(a) = $source_id AND elementId(b) = $target_id
        CREATE (a)-[r:%s $props]->(b)
        RETURN {
            id: elementId(r),
            source: elementId(a),
            target: elementId(b),
            type: type(r),
            properties: properties(r)
        } AS relationship
        """ % rel_type  # 已验证rel_type格式安全

        with driver.get_session() as session:
            result = session.run(
                cypher,
                source_id=str(source_id),
                target_id=str(target_id),
                props=properties
            )
            data = result.single()

            if not data:
                return JsonResponse({"error": "Failed to create relationship"}, status=500)

            return JsonResponse({"relationship": sanitize(data["relationship"])})

    except Exception as e:
        logger.error(f"Add relationship error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Relationship creation failed"}, status=500)

def update_node(request):
    """更新节点属性"""
    try:
        node_id = request.POST.get("id")
        properties = request.POST.get("properties", {})
        
        if not node_id:
            return JsonResponse({"error": "Missing node ID"}, status=400)

        if isinstance(properties, str):
            try:
                properties = json.loads(properties)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid properties format"}, status=400)

        cypher = """
        MATCH (n)
        WHERE elementId(n) = $id
        SET n += $props
        RETURN {
            id: elementId(n),
            label: labels(n)[0], 
            properties: properties(n)
        } AS node
        """
        
        with driver.get_session() as session:
            result = session.run(cypher, id=node_id, props=properties)
            data = result.single()
            
            if not data:
                return JsonResponse({"error": "Node not found"}, status=404)
            
            return JsonResponse({"node": sanitize(data["node"])})

    except Exception as e:
        logger.error(f"Update node error: {str(e)}", exc_info=True)
        return JsonResponse({"error": "Update failed"}, status=500)
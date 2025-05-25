from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# 导入各模块视图
from backend.llms import views
from backend.neo4j.views import (
    initial_graph,
    expand_node,
    search_nodes,
    add_node,
    add_relationship,
    delete_node,
    update_node
)
from backend.hazard_control.views import submit_hazard, hazard_detail, hazard_list,generate_hazard_suggestion,retrieve_subgraph

urlpatterns = [
    path("admin/", admin.site.urls),

    # LLM文件处理接口
    path("api/upload_and_detect/", views.upload_and_detect, name="api-upload"),

    # Neo4j知识图谱接口
    path("api/initial_graph/", initial_graph, name="initial-graph"),
    path("api/expand_node/", expand_node, name="expand-node"),
    path("api/search/", search_nodes, name="node-search"),
    path("api/add_node/", add_node, name="node-add"),
    path("api/delete_node/", delete_node, name="node-delete"),
    path("api/new_relationship/", add_relationship, name="relationship-new"),
    path("api/update_node/", update_node, name="node-update"),

    # Hazard_control接口
    path("api/submit_hazard/", submit_hazard, name="submit-hazard"),
    path('api/hazard/<int:pk>/', hazard_detail, name='hazard-detail'),
    path("api/hazards/", hazard_list),
    path("api/hazards/<int:pk>/suggestions/", generate_hazard_suggestion,
         name="hazard-generate-suggestion"),
    path("api/hazards/<int:pk>/subgraph/", retrieve_subgraph,
         name="hazard-retrieve-subgraph"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
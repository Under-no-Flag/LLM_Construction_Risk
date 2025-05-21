<template>
  <div class="kg-container">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索节点/关系"
        clearable
        @input="handleSearch"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div class="main-wrapper">
      <!-- 左侧操作面板 -->
      <div class="control-panel">
        <!-- 节点操作 -->
        <div class="form-section">
          <h3 class="section-title"><el-icon><CirclePlus /></el-icon> 添加节点</h3>
          <el-form :model="nodeForm" label-width="80px">
            <el-form-item label="节点名称">
              <el-input v-model="nodeForm.label" />
            </el-form-item>
            <el-form-item label="节点类型">
              <el-select v-model="nodeForm.category">
                <el-option label="法规标准" value="Regulation" />
                <el-option label="条款编号" value="Clause" />
                <el-option label="危险源" value="HazardSource" />
                <el-option label="安全风险" value="SafetyRisk" />
                <el-option label="安全隐患" value="SafetyHazard" />
                <el-option label="安全事故" value="SafetyAccident" />
                <el-option label="相关单位与人员" value="RelatedEntity" />
                <el-option label="安全管理措施" value="SafetyMeasure" />
              </el-select>
            </el-form-item>
            <el-form-item
              v-for="(prop, index) in nodeForm.properties"
              :key="index"
              :label="`属性 ${index + 1}`"
            >
              <div class="property-row">
                <el-input v-model="prop.key" placeholder="属性名" style="width: 45%" />
                <el-input v-model="prop.value" placeholder="属性值" style="width: 55%" />
              </div>
            </el-form-item>
            <div class="form-actions">
              <el-button type="primary" plain @click="addProperty">添加属性</el-button>
              <el-button type="primary" @click="submitNode">提交节点</el-button>
            </div>
          </el-form>
        </div>

        <!-- 关系操作 -->
        <div class="form-section">
          <h3 class="section-title"><el-icon><Connection /></el-icon> 添加关系</h3>
          <el-form :model="relationForm" label-width="80px">
            <el-form-item label="起始节点">
              <el-select v-model="relationForm.source" filterable>
                <el-option
                  v-for="node in filteredNodes"
                  :key="node.id"
                  :label="node.data.label || node.data.properties.name || node.id"
                  :value="node.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="目标节点">
              <el-select v-model="relationForm.target" filterable>
                <el-option
                  v-for="node in filteredNodes"
                  :key="node.id"
                  :label="node.data.label || node.data.properties.name || node.id"
                  :value="node.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="关系类型">
              <el-select v-model="relationForm.type">
                <el-option label="包含" value="CONTAINS" />
                <el-option label="职责" value="DUTY" />
                <el-option label="未管控" value="UNCONTROLLED" />
                <el-option label="未控制" value="UNMANAGED" />
                <el-option label="未整改" value="UNCORRECTED" />
                <el-option label="措施" value="MEASURE" />
              </el-select>
            </el-form-item>
            <div class="form-actions">
              <el-button type="primary" @click="submitRelation">提交关系</el-button>
            </div>
          </el-form>
        </div>
      </div>

      <!-- 图谱展示区 -->
      <div class="graph-container">
        <div class="toolbar">
          <el-button-group>
            <el-button @click="zoomIn" title="放大">
              <el-icon><ZoomIn /></el-icon>
            </el-button>
            <el-button @click="zoomOut" title="缩小">
              <el-icon><ZoomOut /></el-icon>
            </el-button>
            <el-button @click="resetView" title="重置视图">
              <el-icon><Refresh /></el-icon>
            </el-button>
            <el-button type="danger" @click="deleteSelected" title="删除选中项">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-button-group>
        </div>
        <div ref="cyElement" class="cy-wrapper"></div>
      </div>
    </div>

    <!-- 节点详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="currentNode.label" width="600px">
      <el-form :model="currentNode" label-width="100px">
        <el-form-item label="节点ID">
          <el-input v-model="currentNode.id" disabled />
        </el-form-item>
        <el-form-item label="节点类型">
          <el-input v-model="currentNode.category" />
        </el-form-item>
        <el-divider>属性信息</el-divider>
        <div v-for="(value, key) in currentNode.properties" :key="key">
          <el-form-item :label="key">
            <el-input v-model="currentNode.properties[key]" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="detailVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNode">保存修改</el-button>
      </template>
    </el-dialog>
  <div v-if="loading" class="loading-overlay">
    <el-icon class="is-loading"><Loading /></el-icon>
    <span>加载中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import cytoscape from 'cytoscape'
import axios from 'axios'
import coseBilkent from 'cytoscape-cose-bilkent'
import _ from 'lodash'
import { 
  Search, CirclePlus, Connection, ZoomIn, 
  ZoomOut, Refresh, Delete, Loading 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 初始化配置
cytoscape.use(coseBilkent)
const cyElement = ref(null)
let cy = null

// 状态管理
const loading = ref(false)
const nodes = ref([])
const edges = ref([])
const searchKeyword = ref('')
const detailVisible = ref(false)
const currentNode = ref({
  id: '',
  label: '',
  category: '',
  properties: {}
})

// 表单数据
const nodeForm = ref({
  label: '',
  category: 'Regulation',
  properties: []
})

const relationForm = ref({
  source: '',
  target: '',
  type: 'CONTAINS'
})

// 计算属性
const filteredNodes = computed(() => {
  return nodes.value.map(node => ({
    id: node.data.id,
    label: node.data.label || node.data.properties.name || node.data.id,
    data: node.data
  }))
})

// 初始化图谱
const initGraph = () => {
  cy = cytoscape({
    container: cyElement.value,
    style: [
      {
        selector: 'node',
        style: {
          'label': (ele) => {
            const props = ele.data('properties');
            return props.name || props.id || ele.data('id'); // 优先name，其次id，最后用节点id
          },
          'width': 80,
          'height': 80,
          'shape': 'ellipse',
          'background-color': '#409EFF',
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': 14,
          'text-wrap': 'ellipsis',
          'text-max-width': 70,
          'border-width': 2,
          'border-color': '#fff'
        }
      },
      {
        selector: 'edge',
        style: {
          'label': 'data(type)',
          'width': 3,
          'line-color': '#909399',
          'target-arrow-shape': 'triangle',
          'target-arrow-color': '#909399',
          'curve-style': 'bezier',
          'font-size': 12
        }
      }
    ],
    layout: {
      name: 'cose-bilkent',
      animate: true,
      randomize: false,
      nodeDimensionsIncludeLabels: true
    },
    minZoom: 0.1,
    maxZoom: 3
  })

  // 节点点击事件
  cy.on('tap', 'node', (e) => {
    const node = e.target
    showNodeDetail(node.data())
  })
}

// 数据加载
const loadInitialData = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/initial_graph/')
    const elements = formatData(response.data)
    
    cy.add(elements)
    nodes.value = elements.filter(el => el.group === 'nodes')
    edges.value = elements.filter(el => el.group === 'edges')
    applyLayout()
  } catch (error) {
    ElMessage.error('数据加载失败: ' + (error.response?.data?.error || error.message))
  } finally {
    loading.value = false
  }
}

// 节点操作
const submitNode = async () => {
  if (!nodeForm.value.category) {
    return ElMessage.warning('请选择节点类型')
  }

  try {
    const params = {
      label: nodeForm.value.category,
      properties: nodeForm.value.properties.reduce((acc, prop) => {
        if (prop.key && prop.value) acc[prop.key] = prop.value
        return acc
      }, {})
    }

    const { data } = await axios.post('/api/add_node/', params)
    
    const newNode = {
      group: 'nodes',
      data: {
        id: data.node.id,
        label: data.node.label,
        category: data.node.label,
        properties: data.node.properties
      }
    }

    cy.add(newNode)
    nodes.value.push(newNode)
    applyLayout()
    resetNodeForm()
    ElMessage.success('节点创建成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '节点创建失败')
  }
}

// 关系操作
const submitRelation = async () => {
  if (!relationForm.value.source || !relationForm.value.target) {
    return ElMessage.warning('请选择起始节点和目标节点')
  }

  try {
    const params = new FormData()
    params.append('source_id', relationForm.value.source)
    params.append('target_id', relationForm.value.target)
    params.append('type', relationForm.value.type)

    const { data } = await axios.post('/api/new_relationship/', params)
    
    const newEdge = {
      group: 'edges',
      data: {
        id: data.relationship.id,
        source: data.relationship.source,
        target: data.relationship.target,
        type: data.relationship.type
      }
    }

    cy.add(newEdge)
    edges.value.push(newEdge)
    applyLayout()
    resetRelationForm()
    ElMessage.success('关系创建成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '关系创建失败')
  }
}

// 删除操作
const deleteSelected = async () => {
  const selected = cy.$(':selected')
  if (selected.length === 0) return

  try {
    await ElMessageBox.confirm('确定删除选中项吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await Promise.all(selected.map(async el => {
      if (el.isNode()) {
        await axios.post('/api/delete_node/', { id: el.data('id') })
        nodes.value = nodes.value.filter(n => n.data.id !== el.data('id'))
      }
      el.remove()
    }))
    
    ElMessage.success('删除成功')
    applyLayout()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }
}

// 节点更新
const saveNode = async () => {
  try {
    const params = new FormData()
    params.append('id', currentNode.value.id)
    params.append('properties', JSON.stringify(currentNode.value.properties))

    const { data } = await axios.post('/api/update_node/', params)
    
    cy.$(`#${currentNode.value.id}`).data({
      ...currentNode.value,
      properties: data.node.properties
    })
    detailVisible.value = false
    ElMessage.success('节点更新成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '更新失败')
  }
}

// 增强搜索
const handleSearch = _.debounce(async () => {
  if (!searchKeyword.value.trim()) {
    await loadInitialData()
    return
  }

  try {
    const { data } = await axios.get('/api/search/', {
      params: { kw: searchKeyword.value.trim() }
    })
    
    cy.elements().remove()
    const elements = formatData({
      nodes: data.nodes,
      edges: []
    })
    
    cy.add(elements)
    nodes.value = elements
    applyLayout()
  } catch (error) {
    ElMessage.error('搜索失败: ' + (error.response?.data?.error || ''))
  }
}, 500)

// 辅助方法
const formatData = (data) => {
  return [
    ...data.nodes.map(node => ({
      group: 'nodes',
      data: {
        id: node.id,
        label: node.label,
        category: node.label,
        properties: node.properties
      }
    })),
    ...data.edges.map(edge => ({
      group: 'edges',
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: edge.type
      }
    }))
  ]
}

const applyLayout = () => {
  cy.layout({
    name: 'cose-bilkent',
    animate: true,
    animationDuration: 100
  }).run()
}

const addProperty = () => {
  nodeForm.value.properties.push({ key: '', value: '' })
}

const resetNodeForm = () => {
  nodeForm.value = {
    label: '',
    category: 'Law',
    properties: []
  }
}

const resetRelationForm = () => {
  relationForm.value = {
    source: '',
    target: '',
    type: 'CONTAINS'
  }
}

onMounted(() => {
  initGraph()
  loadInitialData()
})
</script>

<style scoped>
/* 新增样式 */
.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  background: rgba(255, 255, 255, 0.9);
  padding: 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.loading-overlay .el-icon {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 优化选中样式 */
:selected {
  border-color: #f56c6c !important;
  border-width: 3px !important;
  transition: border-color 0.3s ease;
}

.kg-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.search-bar {
  padding: 16px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.main-wrapper {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.control-panel {
  width: 360px;
  padding: 16px;
  background: #fff;
  border-right: 1px solid #ebeef5;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.section-title {
  margin: 0 0 16px;
  font-size: 16px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.graph-container {
  flex: 1;
  position: relative;
}

.cy-wrapper {
  width: 100%;
  height: 100%;
  background: #fff;
}

.toolbar {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 100;
  background: rgba(255,255,255,0.9);
  padding: 8px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.property-row {
  display: flex;
  gap: 8px;
}

.form-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
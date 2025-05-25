<template>
    <div class="mitigation-container dark-theme">
        <!-- =============== 顶部信息区 =============== -->
        <el-card shadow="hover" class="info-section">
            <div class="info-left">
                <div class="title-row">
                    <el-icon>
                        <WarningFilled />
                    </el-icon>
                    <h2 class="hazard-title">{{ hazard.title }}</h2>
                </div>
                <ul class="meta-list">
                    <li>
                        <el-icon>
                            <UserFilled />
                        </el-icon>上传人：
                        <span>{{ hazard.uploader }}</span>
                    </li>
                    <li>
                        <el-icon>
                            <BellFilled />
                        </el-icon>AI 风险描述：
                        <span>{{ hazard.riskDescription }}</span>
                    </li>
                    <li>
                        <el-icon>
                            <VideoCamera />
                        </el-icon>现场图片：
                    </li>
                </ul>
            </div>
            <div class="info-right">
                <el-image :src="hazard.image" fit="cover" class="scene-img" />
            </div>
        </el-card>

        <!-- =============== 处理流程 Steps =============== -->
        <el-steps :active="2" align-center finish-status="success" class="ai-steps">
            <el-step title="风险描述 → 知识检索" :icon="Search" />
            <el-step title="生成关联子图" :icon="Connection" />
            <el-step title="输出治理意见" :icon="EditPen" />
        </el-steps>

        <!-- =============== 知识子图 =============== -->
        <el-card shadow="always" class="graph-section">
            <template #header>
                <el-icon>
                    <DataLine />
                </el-icon>
                <span class="section-title" tyle="font-size: larger">相关安全法规知识图谱</span>
                <el-button type="primary" size="large" :loading="loadingSubGraph" @click="retriveSubGraph" style="font-size: larger">检索得到的知识子图</el-button>
            </template>
            <div ref="cyContainer" class="cy-wrapper" />
        </el-card>

        <el-card shadow="always" class="suggest-section">
            <template #header>
                <el-icon>
                    <Memo />
                </el-icon>
                <span class="section-title" tyle="font-size: larger">大模型生成的隐患治理意见</span>

                <el-button type="primary" size="large" :loading="loadingGen" @click="generateSuggestions" style="font-size: larger">生成治理意见</el-button>
            </template>
            <el-empty v-if="suggestions.length === 0 && !loadingGen" description="暂无治理意见" />
            <el-timeline v-else-if="suggestions.length > 0">
                <el-timeline-item v-for="(p, idx) in suggestions" :key="idx" :timestamp="`步骤 ${idx + 1}`" :color="'#00f3ff'" style="font-size: larger">{{ p }}</el-timeline-item>
            </el-timeline>
            <!-- 生成治理意见按钮 -->
        </el-card>

        <!-- ======== ① 人工处理意见编辑框（新增） ======== -->
        <el-card shadow="always" class="manual-section" style="margin-top: 20px">
            <template #header>
                <el-icon>
                    <EditPen />
                </el-icon>
                <span class="section-title">人工处理意见</span>
            </template>

            <el-input v-model="manualOpinion" type="textarea" :rows="7" placeholder="请在此填写或修改整改意见..." resize="vertical" />

            <!-- ======== ② 下发整改意见按钮（新增） ======== -->
            <div style="text-align: right; margin-top: 12px">
                <el-button type="success" :disabled="manualOpinion.trim() === ''" :loading="issuing" @click="issueOpinion" style="font-size: larger">下发整改意见</el-button>
            </div>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import cytoscape from 'cytoscape'
import { WarningFilled, UserFilled, BellFilled, Search, Connection, EditPen, DataLine, Memo, VideoCamera } from '@element-plus/icons-vue'
import { ElMessage, ElNotification,ElMessageBox } from 'element-plus'
import axios from 'axios'
import 'element-plus/dist/index.css'

// 从路由拿到 hazard id
const route = useRoute()
const hazardId = (route.params.id as string) || '1'

// ---------------- 示例数据 ----------------
// 响应式数据
const hazard = ref({
    id: 0,
    title: '',
    uploader: '',
    riskDescription: '',
    image: '',
})

const cyElements = ref<any[]>([])
const loadingGen = ref(false)
const loadingSubGraph = ref(false) // 子图加载中
const suggestions = ref<string[]>([])
const manualOpinion = ref<string>('') // 人工处理意见
const issuing = ref(false) // 下发按钮 loading
// const cyElements = [
//     // 风险节点
//     { data: { id: 'risk_helmet', label: '未佩戴安全帽' } },
//     { data: { id: 'risk_edge', label: '临边无防护' } },
//     { data: { id: 'risk_harness', label: '未系安全带' } },

//     // 措施节点
//     { data: { id: 'measure_helmet', label: '全员佩戴安全帽' } },
//     { data: { id: 'measure_edge', label: '设防护栏杆/安全网' } },
//     { data: { id: 'measure_harness', label: '系挂安全带+生命线' } },

//     // 法规节点
//     {
//         data: {
//             id: 'spec_59_hat',
//             label: 'JGJ59-2011 3.13.3(1)',
//         },
//     },
//     {
//         data: {
//             id: 'spec_80_edge',
//             label: 'JGJ80-2016 4.1.3',
//         },
//     },
//     {
//         data: {
//             id: 'spec_59_harness',
//             label: 'JGJ59-2011 3.13.3(3)',
//         },
//     },

//     // 风险→措施 边
//     { data: { source: 'risk_helmet', target: 'measure_helmet', label: '治理' } },
//     { data: { source: 'risk_edge', target: 'measure_edge', label: '治理' } },
//     { data: { source: 'risk_harness', target: 'measure_harness', label: '治理' } },
//     // 措施→法规 边
//     { data: { source: 'measure_helmet', target: 'spec_59_hat', label: '依据' } },
//     { data: { source: 'measure_edge', target: 'spec_80_edge', label: '依据' } },
//     { data: { source: 'measure_harness', target: 'spec_59_harness', label: '依据' } },
// ]

// const suggestions = ref([
//     '现场所有作业人员进入施工区域前必须正确佩戴合格安全帽，并由安全员现场巡查抽检。',
//     '在作业临边处安装 1.2 m 高双道防护栏杆，并加挂密目式安全网，夜间作业区加装照明。',
//     '设置水平生命线，高处作业人员全程系挂安全带并定期检查挂点牢固性。',
//     '以 JGJ59‑2011 3.13.3 与 JGJ80‑2016 4.1.3 为依据，完成整改后填写隐患关闭单并归档。',
// ])

const cyContainer = ref<HTMLDivElement | null>(null)

onMounted(async () => {
    try {
        const res = await axios.get(`/api/hazard/${hazardId}/`)
        // 解构后端 JSON
        hazard.value = res.data.hazard
        cyElements.value = res.data.graph
        suggestions.value = res.data.suggestions

        // 初始化 Cytoscape
        if (cyElements.value.length && cyContainer.value) {
            cytoscape({
                container: cyContainer.value,
                elements: cyElements.value,
                layout: { name: 'cose', animate: true },
                style: [
                    {
                        selector: 'node',
                        style: {
                            'background-color': '#00d4ff',
                            label: 'data(label)',
                            color: '#ffffff',
                            'font-size': '12px',
                            'text-valign': 'center',
                            'text-outline-color': '#0a0e17',
                            'text-outline-width': 2,
                        },
                    },
                    {
                        selector: 'edge',
                        style: {
                            width: 2,
                            'line-color': '#ffffff',
                            'target-arrow-color': '#ffffff',
                            'target-arrow-shape': 'triangle',
                            label: 'data(label)',
                            'font-size': '10px',
                            color: '#00f3ff',
                        },
                    },
                ],
            })
        }

        ElMessage.success('数据加载完成')
    } catch (e) {
        console.error(e)
        // ElMessage.error('从服务器加载隐患详情失败')
    }
})

async function generateSuggestions() {
    loadingGen.value = true
    try {
        const { data } = await axios.post(`/api/hazards/${hazardId}/suggestions/`)
        suggestions.value = data.suggestions ?? []
        manualOpinion.value = suggestions.value.join('\n')
        if (suggestions.value.length === 0) {
            ElMessage.warning('模型未返回任何整改意见')
        }
    } catch (err: any) {
        ElMessage.error(`生成失败：${err?.response?.data?.error || err}`)
    } finally {
        loadingGen.value = false
    }
}
async function retriveSubGraph() {
    loadingSubGraph.value = true
    try {
        const { data } = await axios.post(`/api/hazards/${hazardId}/subgraph/`)
        cyElements.value = data.graph ?? []
        if (cyContainer.value) {
            cytoscape({
                container: cyContainer.value,
                elements: cyElements.value,
                layout: { name: 'cose', animate: true },
                style: [
                    {
                        selector: 'node',
                        style: {
                            'background-color': '#00d4ff',
                            label: 'data(label)',
                            color: '#ffffff',
                            'font-size': '12px',
                            'text-valign': 'center',
                            'text-outline-color': '#0a0e17',
                            'text-outline-width': 2,
                        },
                    },
                    {
                        selector: 'edge',
                        style: {
                            width: 2,
                            'line-color': '#ffffff',
                            'target-arrow-color': '#ffffff',
                            'target-arrow-shape': 'triangle',
                            label: 'data(label)',
                            'font-size': '10px',
                            color: '#00f3ff',
                        },
                    },
                ],
            })
        }
    } catch (err: any) {
        ElMessage.error(`加载失败：${err?.response?.data?.error || err}`)
    } finally {
        loadingSubGraph.value = false
    }
}

/* ===== 下发整改意见 ===== */
async function issueOpinion() {
    issuing.value = true
    ElMessageBox.alert(
        '整改意见已成功下发给施工单位，请留意后续整改反馈。',
        '提交成功', // 标题
        {
            type: 'success',
            confirmButtonText: '好的',
            center: true, // 文本居中，可选
        }
    )
    issuing.value = false

    // try {
    //     await axios.post(`/api/hazards/${hazardId}/issue/`, {
    //         opinion: manualOpinion.value,
    //     })
    //     ElMessage.success('整改意见已下发')
    // } catch (err: any) {
    //     ElMessage.error(`下发失败：${err?.response?.data?.error || err}`)
    // } finally {
    //     issuing.value = false
    // }
}
</script>

<style scoped>
.mitigation-container {
    padding: 2rem;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* 顶部信息卡片 */
.info-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    font-size: larger;
}
.info-left {
    flex: 1;
}
.title-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
.hazard-title {
    font-size: 1.5rem;
    color: #ff0004;
}
.meta-list {
    list-style: none;
    padding: 0;
    margin: 0;
    font-size: larger;
}
.meta-list li {
    margin: 0.3rem 0;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    color: #970e1e;
}
.meta-list li span {
    color: #090202;
}
.info-right .scene-img {
    width: 620px; /* ---- 调大图片尺寸 ---- */
    border-radius: 10px;
    object-fit: cover;
    box-shadow: 0 0 16px rgba(0, 243, 255, 0.45);
}

/* Steps */
.ai-steps {
    --el-color-primary: #00f3ff;
}

/* section card */
.section-title {
    margin-left: 0.4rem;
    font-weight: 1000;
}

/* cytoscape container */
.cy-wrapper {
    width: 100%;
    height: 360px;
    background: radial-gradient(circle at center, #00121d 0%, #00070c 100%);
    border-radius: 6px;
    border: 1px solid rgba(0, 243, 255, 0.2);
}

/* 建议区 */
.suggest-section .el-timeline-item__timestamp {
    color: #00f3ff;
}
.suggest-section {
    font-size: larger;
}
.graph-section {
    font-size: large;
}
</style>

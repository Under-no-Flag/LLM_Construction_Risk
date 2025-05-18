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
                <span class="section-title">检索得到的知识子图</span>
            </template>
            <div ref="cyContainer" class="cy-wrapper" />
        </el-card>

        <!-- =============== 治理建议 =============== -->
        <el-card shadow="always" class="suggest-section">
            <template #header>
                <el-icon>
                    <Memo />
                </el-icon>
                <span class="section-title">大模型生成的隐患治理意见</span>
            </template>
            <el-timeline>
                <el-timeline-item v-for="(p, idx) in suggestions" :key="idx" :timestamp="`步骤 ${idx + 1}`" :color="'#00f3ff'" style="font-size: large">{{ p }}</el-timeline-item>
            </el-timeline>
        </el-card>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import cytoscape from 'cytoscape'
import { WarningFilled, UserFilled, BellFilled, Search, Connection, EditPen, DataLine, Memo,VideoCamera } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ---------------- 示例数据 ----------------
const hazard = {
    id: 1,
    title: '施工点A存在施工安全隐患',
    uploader: '张三',
    riskDescription: '仅有 1 人戴安全帽，其余人员未佩戴;作业面在夜间、临边无任何防护栏杆或安全网;	未见系挂式安全带或水平生命线',
    image: '/src/statics/demo_images/1.png',
}

const cyElements = [
    // 风险节点
    { data: { id: 'risk_helmet', label: '未佩戴安全帽' } },
    { data: { id: 'risk_edge', label: '临边无防护' } },
    { data: { id: 'risk_harness', label: '未系安全带' } },

    // 措施节点
    { data: { id: 'measure_helmet', label: '全员佩戴安全帽' } },
    { data: { id: 'measure_edge', label: '设防护栏杆/安全网' } },
    { data: { id: 'measure_harness', label: '系挂安全带+生命线' } },

    // 法规节点
    {
        data: {
            id: 'spec_59_hat',
            label: 'JGJ59-2011 3.13.3(1)',
        },
    },
    {
        data: {
            id: 'spec_80_edge',
            label: 'JGJ80-2016 4.1.3',
        },
    },
    {
        data: {
            id: 'spec_59_harness',
            label: 'JGJ59-2011 3.13.3(3)',
        },
    },

    // 风险→措施 边
    { data: { source: 'risk_helmet', target: 'measure_helmet', label: '治理' } },
    { data: { source: 'risk_edge', target: 'measure_edge', label: '治理' } },
    { data: { source: 'risk_harness', target: 'measure_harness', label: '治理' } },
    // 措施→法规 边
    { data: { source: 'measure_helmet', target: 'spec_59_hat', label: '依据' } },
    { data: { source: 'measure_edge', target: 'spec_80_edge', label: '依据' } },
    { data: { source: 'measure_harness', target: 'spec_59_harness', label: '依据' } },
]

const suggestions = ref([
    '现场所有作业人员进入施工区域前必须正确佩戴合格安全帽，并由安全员现场巡查抽检。',
    '在作业临边处安装 1.2 m 高双道防护栏杆，并加挂密目式安全网，夜间作业区加装照明。',
    '设置水平生命线，高处作业人员全程系挂安全带并定期检查挂点牢固性。',
    '以 JGJ59‑2011 3.13.3 与 JGJ80‑2016 4.1.3 为依据，完成整改后填写隐患关闭单并归档。',
])

const cyContainer = ref<HTMLDivElement | null>(null)

onMounted(() => {
    if (cyContainer.value) {
        cytoscape({
            container: cyContainer.value,
            elements: cyElements,
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
    ElMessage.success('知识图谱检索完成，已生成治理意见')
})
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

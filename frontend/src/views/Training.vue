<template>
  <div class="page-card">
    <h2 class="page-title">Algorithm Training</h2>
    <el-form :model="form" label-width="160px" class="training-form" v-loading="loading">
      
      <el-row :gutter="24">
        <el-col :span="18">
          <el-form-item label="选择数据集（Dataset）">
            <el-select v-model="form.dataset" placeholder="选择生成的数据集" class="w-100">
              <el-option v-for="ds in datasets" :key="ds" :label="ds" :value="ds" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-button @click="fetchDatasets" :icon="Refresh" class="w-100">刷新列表</el-button>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="算法（Algorithm）">
            <el-select v-model="form.algo" class="w-100">
              <el-option v-for="a in algos" :key="a" :label="a" :value="a" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="模型（Model）">
            <el-select v-model="form.model" class="w-100">
              <el-option v-for="m in models" :key="m" :label="m" :value="m" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="全局轮数（Global Rounds）">
            <el-input v-model="form.gr" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="GPU ID ">
            <el-input v-model="form.did" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="随机种子（Random Seed）">
            <el-input v-model="form.seed" />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="submit-action">
        <el-button type="success" size="large" @click="onSubmit" class="action-btn">
          <el-icon class="el-icon--left"><VideoPlay /></el-icon>
          开始训练
        </el-button>
      </div>

    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getDatasetList, startTraining } from '../api'
import { ElMessage } from 'element-plus'
import { Refresh, VideoPlay } from '@element-plus/icons-vue'

const loading = ref(false)
const datasets = ref([])

const algos = ["CReFF", "CLIP2FL", "CCVR", "RUCR", "FedETF", "FedLoGe", "FedNH", "FedLC", "FedGraB", "FedAvg", "FedProx", "FedIC"]
const models = ["ResNet8", "ResNet18", "ResNet20", "ResNet34", "CNN", "MobileNet"]

const form = reactive({
  dataset: '',
  algo: 'CReFF',
  model: 'ResNet8',
  gr: '200',
  did: '0',
  seed: '7'
})

const fetchDatasets = async () => {
  try {
    const res = await getDatasetList()
    datasets.value = res.data.datasets || []
    if (datasets.value.length > 0 && !form.dataset) {
      form.dataset = datasets.value[0]
    }
  } catch (err) {
    //
  }
}

const onSubmit = async () => {
  if (!form.dataset) {
    ElMessage.warning('Please select a dataset first.')
    return
  }
  
  try {
    loading.value = true
    const res = await startTraining(form)
    ElMessage.success('Training started!')
  } catch (error) {
    //
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDatasets()
})
</script>

<style scoped>
.page-title {
  margin-top: 0;
  margin-bottom: 30px;
  font-weight: 600;
  color: #1f2f3d;
  font-size: 26px;
  position: relative;
  padding-left: 14px;
}

.page-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 4px;
  bottom: 4px;
  width: 4px;
  background: #67c23a;
  border-radius: 2px;
}

.training-form {
  max-width: 950px;
}

.w-100 {
  width: 100%;
}

.submit-action {
  margin-top: 50px;
  text-align: center;
}

.action-btn {
  width: 260px;
  height: 48px;
  border-radius: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #67c23a, #5daf34);
  border: none;
  box-shadow: 0 6px 16px rgba(103, 194, 58, 0.3);
  transition: all 0.3s;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(103, 194, 58, 0.4);
}

.hint-text {
  margin-top: 16px;
  font-size: 13px;
  color: #a8abb2;
}
</style>

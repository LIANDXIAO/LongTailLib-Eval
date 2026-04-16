<template>
  <div class="page-card">
    <h2 class="page-title">Experiment Results Comparison</h2>
    <el-form :model="form" class="comparison-form" v-loading="loading">
      
      <el-row :gutter="24" class="align-center">
        <el-col :span="16">
          <el-form-item label="Select Experiment Group" label-width="180px">
            <el-select v-model="form.dataset" placeholder="Select dataset group to compare" class="w-100">
              <el-option v-for="ds in datasets" :key="ds" :label="ds" :value="ds" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-button @click="fetchDatasets" :icon="Refresh">Refresh List</el-button>
        </el-col>
      </el-row>

      <div class="submit-action">
        <el-button type="primary" size="large" @click="onSubmit" class="action-btn">
          <el-icon class="el-icon--left"><DataAnalysis /></el-icon>
          Generate Comparison Plot
        </el-button>
      </div>

    </el-form>

    <div v-if="imgSrc" class="result-image-container">
      <el-divider>Comparison Result</el-divider>
      <el-image :src="imgSrc" :preview-src-list="[imgSrc]" class="result-image" fit="contain">
        <template #placeholder>
          <div class="image-slot">Loading data ...</div>
        </template>
      </el-image>
      <div class="hint-text mt-15 text-center">Click image to enlarge. Numerical table is printed in the Log Console below.</div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getResultsList, compareResults } from '../api'
import { ElMessage } from 'element-plus'
import { Refresh, DataAnalysis } from '@element-plus/icons-vue'

const loading = ref(false)
const datasets = ref([])
const imgSrc = ref('')

const form = reactive({
  dataset: ''
})

const fetchDatasets = async () => {
  try {
    const res = await getResultsList()
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
    ElMessage.warning('Please select an experiment group.')
    return
  }
  
  try {
    loading.value = true
    imgSrc.value = ''
    const res = await compareResults(form)
    imgSrc.value = res.data.image_base64
    ElMessage.success('Comparison plot generated successfully.')
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
  background: #e6a23c;
  border-radius: 2px;
}

.comparison-form {
  max-width: 900px;
}

.w-100 {
  width: 100%;
}

.align-center {
  align-items: center;
}

.submit-action {
  margin-top: 40px;
}

.action-btn {
  width: 280px;
  height: 48px;
  border-radius: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
  background: linear-gradient(135deg, #e6a23c, #cf9236);
  border: none;
  box-shadow: 0 6px 16px rgba(230, 162, 60, 0.3);
  transition: all 0.3s;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(230, 162, 60, 0.4);
}

.result-image-container {
  margin-top: 40px;
  animation: fadeIn 0.5s ease-in-out;
}

.result-image {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
  background: white;
}

.mt-15 {
  margin-top: 15px;
}

.text-center {
  text-align: center;
}

.hint-text {
  font-size: 13px;
  color: #a8abb2;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

<template>
  <div class="page-card">
    <h2 class="page-title">数据集生成</h2>
    <el-form :model="form" label-width="160px" class="dataset-form" v-loading="loading">
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="目标数据集（Target）">
            <el-select v-model="form.ds_name" placeholder="Select dataset" class="w-100">
              <el-option label="Cifar10" value="Cifar10" />
              <el-option label="Cifar100" value="Cifar100" />
              <el-option label="MNIST" value="MNIST" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="分布类型（Distribution）">
            <el-select v-model="form.ds_niid" class="w-100">
              <el-option label="non-i.i.d" value="noniid" />
              <el-option label="i.i.d" value="iid" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="数据量平衡（Balance）">
            <el-select v-model="form.ds_balance" class="w-100">
              <el-option label="Unbalanced (-)" value="-" />
              <el-option label="Balanced" value="balance" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="划分策略（Partition）">
            <el-select v-model="form.ds_partition" class="w-100">
              <el-option label="Dirichlet (dir)" value="dir" />
              <el-option label="Pat" value="pat" />
              <el-option label="Exdir" value="exdir" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <div class="section-divider">
        <span class="divider-text">长尾设置</span>
      </div>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="启动长尾">
            <el-switch
              v-model="form.ds_longtail"
              active-value="longtail"
              inactive-value="normal"
              active-text="ON"
              inactive-text="OFF">
            </el-switch>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="长尾类型">
            <el-select v-model="form.ds_type" :disabled="form.ds_longtail !== 'longtail'" class="w-100">
              <el-option label="Global" value="global" />
              <el-option label="Local" value="local" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="不平衡因子(IF)">
            <el-input v-model="form.ds_if" :disabled="form.ds_longtail !== 'longtail'" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Dirichlet Alpha">
            <el-input v-model="form.ds_alpha" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="客户端数量">
            <el-input v-model="form.ds_clients" />
          </el-form-item>
        </el-col>
      </el-row>

      <div class="submit-action">
        <el-button type="primary" size="large" @click="onSubmit" class="action-btn">
          <el-icon class="el-icon--left"><Cpu /></el-icon>
          生成数据集
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { generateDataset } from '../api'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const form = reactive({
  ds_name: 'Cifar10',
  ds_niid: 'noniid',
  ds_balance: '-',
  ds_partition: 'dir',
  ds_longtail: 'longtail',
  ds_type: 'global',
  ds_if: '50',
  ds_alpha: '0.5',
  ds_clients: '20'
})

const onSubmit = async () => {
  try {
    loading.value = true
    const res = await generateDataset(form)
    ElMessage.success('生成命令提交成功.')
  } catch (error) {
    //
  } finally {
    loading.value = false
  }
}
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
  background: #409EFF;
  border-radius: 2px;
}

.dataset-form {
  max-width: 950px;
}

.w-100 {
  width: 100%;
}

.section-divider {
  position: relative;
  margin: 30px 0 24px;
  display: flex;
  align-items: center;
}

.section-divider::before {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ebeef5;
}

.section-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ebeef5;
}

.divider-text {
  padding: 0 16px;
  font-size: 14px;
  font-weight: 500;
  color: #909399;
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
  background: linear-gradient(135deg, #409EFF, #3a8ee6);
  border: none;
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.4);
}

.hint-text {
  margin-top: 16px;
  font-size: 13px;
  color: #a8abb2;
}
</style>

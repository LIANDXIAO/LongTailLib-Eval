<template>
  <div class="log-console-wrapper" :class="{ 'minimized': isMinimized }">
    <div class="console-header" @click="isMinimized = !isMinimized">
      <div class="header-left">
        <el-icon><Monitor /></el-icon>
        <span>Console Log</span>
        <span class="status-indicator" :class="isConnected ? 'connected' : 'disconnected'"></span>
      </div>
      <div class="header-right" @click.stop>
        <el-button type="danger" size="small" plain @click="stopProcessing">Stop Task</el-button>
        <el-button size="small" plain @click="clearLog">Clear</el-button>
        <el-icon class="toggle-icon" @click="isMinimized = !isMinimized">
          <ArrowDown v-if="!isMinimized" />
          <ArrowUp v-else />
        </el-icon>
      </div>
    </div>
    
    <div class="console-body" ref="logBody">
      <pre class="log-content">{{ logs }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { stopTask } from '../api'
import { ElMessage } from 'element-plus'

const logs = ref('')
const isMinimized = ref(false)
const logBody = ref(null)
const isConnected = ref(false)
let ws = null

const connectWs = () => {
  ws = new WebSocket('ws://localhost:8000/ws/logs')
  
  ws.onopen = () => {
    isConnected.value = true
  }

  ws.onmessage = (event) => {
    logs.value += event.data
  }
  
  ws.onclose = () => {
    isConnected.value = false
    setTimeout(connectWs, 3000)
  }
}

watch(logs, () => {
  nextTick(() => {
    if (logBody.value) {
      logBody.value.scrollTop = logBody.value.scrollHeight
    }
  })
})

const clearLog = () => {
  logs.value = ''
}

const stopProcessing = async () => {
  try {
    const res = await stopTask()
    ElMessage.success(res.data.message)
  } catch (error) {
    // handled
  }
}

onMounted(() => {
  connectWs()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
.log-console-wrapper {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 280px;
  background-color: #1e1e1e;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  border-top: 1px solid #333;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.2);
}

.log-console-wrapper.minimized {
  transform: translateY(240px);
}

.console-header {
  height: 40px;
  background-color: #2d2d2d;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  cursor: pointer;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 14px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: 5px;
}

.status-indicator.connected {
  background-color: #67C23A;
  box-shadow: 0 0 5px #67C23A;
}

.status-indicator.disconnected {
  background-color: #F56C6C;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-icon {
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.toggle-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.console-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px 20px;
}

.log-content {
  margin: 0;
  color: #a6e22e;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}

.console-body::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.console-body::-webkit-scrollbar-track {
  background: #1e1e1e;
}

.console-body::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.console-body::-webkit-scrollbar-thumb:hover {
  background: #777;
}
</style>

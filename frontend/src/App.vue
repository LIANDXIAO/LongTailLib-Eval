<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="logo">
        <el-icon :size="24" color="#409eff"><DataLine /></el-icon>
        <span>LongTailLib Platform</span>
      </div>
      <el-menu mode="horizontal" :default-active="$route.path" router class="nav-menu" :ellipsis="false">
        <el-menu-item index="/dataset">Dataset</el-menu-item>
        <el-menu-item index="/training">Training</el-menu-item>
        <el-menu-item index="/comparison">Comparison</el-menu-item>
      </el-menu>
    </el-header>

    <el-main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <!-- Global Log Console -->
    <LogConsole />
  </el-container>
</template>

<script setup>
import LogConsole from './components/LogConsole.vue'
</script>

<style>
body {
  margin: 0;
  font-family: 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  background-color: #f5f7fa;
  color: #303133;
}

.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: #ffffff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 60px;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.nav-menu {
  border-bottom: none !important;
  flex: 1;
  justify-content: flex-end;
}

.main-content {
  flex: 1;
  padding: 30px 40px;
  overflow: hidden;
  padding-bottom: 300px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.page-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  border: none;
  background: white;
  padding: 30px;
}
</style>

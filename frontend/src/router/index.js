import { createRouter, createWebHistory } from 'vue-router'
import Dataset from '../views/Dataset.vue'
import Training from '../views/Training.vue'
import Comparison from '../views/Comparison.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dataset'
    },
    {
      path: '/dataset',
      name: 'Dataset',
      component: Dataset
    },
    {
      path: '/training',
      name: 'Training',
      component: Training
    },
    {
      path: '/comparison',
      name: 'Comparison',
      component: Comparison
    }
  ]
})

export default router

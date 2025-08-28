import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    { path: '/etiquetado',
      name: 'Etiquetado',
      component: () => import('../views/Etiquetado.vue') },
    { path: '/database',
      name: 'Database',
      component: () => import('../views/Database.vue') },
    { path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue') },
    { 
      path: '/AI',
      name: 'AI',
      component: () => import('../views/AI/AI_Index.vue'), 
      children:[
        {
          path: 'train',
          name: 'AITrain',
          component: () => import('../views/AI/AI_Train.vue')
        },
        {
          path: 'inference',
          name: 'AIInference',
          component: () => import('../views/AI/AI_Inference.vue')
        }
      ]
    }
  ],
})

export default router

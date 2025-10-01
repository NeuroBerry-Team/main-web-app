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
    { 
      path: '/etiquetado',
      name: 'Etiquetado',
      component: () => import('../views/Etiquetado.vue') 
    },
    { 
      path: '/database',
      name: 'Database',
      component: () => import('../views/Database.vue') 
    },
    { 
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue') 
    },
    { 
      path: '/modulo1',
      name: 'Modulo1',
      component: () => import('../views/Modulos/Modulo1.vue') 
    },
    { 
      path: '/modulo2',
      name: 'Modulo2',
      component: () => import('../views/Modulos/Modulo2.vue') 
    },
    { 
      path: '/modulo3',
      name: 'Modulo3',
      component: () => import('../views/Modulos/Modulo3.vue') 
    },
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
    },
    {
      path: '/profile/settings',
      name: 'ProfileSettings',
      component: () => import('../views/user/ProfileSettings.vue')
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/user/Profile.vue'),
      children:[
        {
          path: 'activity',
          name: 'ProfileActivity',
          component: () => import('../views/user/ProfileActivity.vue'),
          children:[
            {
              path: 'metrics',
              name: 'ProfileActivityMetrics',
              component: () => import('../views/user/ProfileActivityMetrics.vue')
            },
            {
              path: 'logs',
              name: 'ProfileActivityLogs',
              component: () => import('../views/user/ProfileActivityLogs.vue')
            },
            {
              path: 'inferences',
              name: 'ProfileActivityInferences',
              component: () => import('../views/user/ProfileActivityInferences.vue')
            }
          ]
        }
      ]
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('../views/admin/AdminMain.vue')
    }
  ],
})

export default router
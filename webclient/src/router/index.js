import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Test from '../views/IATest.vue'
import Database from '../views/Database.vue'
import Login from '../views/Login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    { path: '/iatest',
      name: 'IATest',
      component: () => import('../views/IATest.vue') },
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
      path: '/temp',
      name: 'temp',
      component: () => import('../views/TempView.vue') },
  ],
})

export default router

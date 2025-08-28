<script setup>
import { RouterLink } from 'vue-router'
import { useAuth } from '../composables/use_auth.js'
const { isLoggedIn, user, isAdmin, logout } = useAuth()

const handleLogout = async () => {
  if (confirm('Are you sure you want to logout?')) {
    await logout()
  }
}
</script>
<template>
  <nav class="flex flex-wrap gap-4 items-center justify-center">
    <RouterLink
      to="/"
      class="px-6 py-2 rounded-full bg-white/10 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-white/30 hover:-translate-y-0.5 hover:scale-105"
    >Inicio</RouterLink>
    <RouterLink
      to="/about"
      class="px-6 py-2 rounded-full bg-white/10 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-white/30 hover:-translate-y-0.5 hover:scale-105"
    >Proyecto</RouterLink>
    <RouterLink
      to="/database"
      class="px-6 py-2 rounded-full bg-white/10 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-white/30 hover:-translate-y-0.5 hover:scale-105"
    >Database</RouterLink>
    <RouterLink
      to="/etiquetado"
      class="px-6 py-2 rounded-full bg-white/10 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-white/30 hover:-translate-y-0.5 hover:scale-105"
    >Etiquetado</RouterLink>

    <!-- Show application link only if logged in -->
    <RouterLink
      v-if="isLoggedIn"
      to="/AI"
      class="px-6 py-2 rounded-full bg-blue-600/20 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-blue-600/40 hover:-translate-y-0.5 hover:scale-105"
    >Aplicación</RouterLink>

    <!-- Show admin features if user is admin or superadmin -->
    <RouterLink
      v-if="isAdmin"
      to="/admin"
      class="px-6 py-2 rounded-full bg-purple-600/20 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-purple-600/40 hover:-translate-y-0.5 hover:scale-105"
    >Admin</RouterLink>

    <!-- Authentication links -->
    <RouterLink
      v-if="!isLoggedIn"
      to="/login"
      class="px-6 py-2 rounded-full bg-green-600/20 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-green-600/40 hover:-translate-y-0.5 hover:scale-105"
    >Login</RouterLink>
    <button
      v-if="isLoggedIn"
      @click="handleLogout"
      class="px-6 py-2 rounded-full bg-red-600/20 text-white font-medium text-base transition-all duration-300 shadow-md text-center hover:bg-red-600/40 hover:-translate-y-0.5 hover:scale-105 flex items-center gap-2"
    >
      Logout
      <span v-if="user?.role" class="ml-1 text-xs bg-white/20 px-2 py-1 rounded">{{ user.role }}</span>
    </button>
  </nav>
</template>
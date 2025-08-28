<script setup>
import { RouterLink} from 'vue-router'
import { useAuth } from '../composables/use_auth.js'
const { isLoggedIn, user, isAdmin, logout } = useAuth()

const handleLogout = async () => {
  if (confirm('Are you sure you want to logout?')) {
    await logout()
  }
}
</script>
<template>
    <!-- MENU -->
    <nav>
        <RouterLink to="/" class="nav-button">Inicio</RouterLink>
        <RouterLink to="/about" class="nav-button">Proyecto</RouterLink>
        <RouterLink to="/database" class="nav-button">Database</RouterLink>
        <RouterLink to="/etiquetado" class="nav-button">Etiquetado</RouterLink>
        
        <!-- Show application link only if logged in -->
        <RouterLink v-if="isLoggedIn" to="/AI" class="nav-button">Aplicación</RouterLink>
        
        <!-- Show admin features if user is admin -->
        <RouterLink v-if="isAdmin" to="/admin" class="nav-button admin-link">Admin</RouterLink> <!-- TODO: Implement admin panel -->

        <!-- Authentication links -->
        <RouterLink v-if="!isLoggedIn" to="/login" class="nav-button login-button">Login</RouterLink>
        <button v-if="isLoggedIn" @click="handleLogout" class="nav-button logout-button">
        Logout
        <span v-if="user?.role" class="user-role">({{ user.role }})</span>
        </button>
    </nav>
</template>
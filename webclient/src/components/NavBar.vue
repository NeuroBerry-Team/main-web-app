<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="hamburger-container">
        <button @click="menuOpen = !menuOpen" class="hamburger-btn" aria-label="Toggle menu">
          ☰
        </button>
      </div>

      <div class="nav-links-wrapper" :class="{ 'open': menuOpen }">
        <RouterLink to="/" class="nav-btn" @click="menuOpen = false">Inicio</RouterLink>

        <RouterLink v-if="isLoggedIn" to="/about" class="nav-btn" @click="menuOpen = false">Proyecto</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/database" class="nav-btn" @click="menuOpen = false">Database</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/etiquetado" class="nav-btn" @click="menuOpen = false">Etiquetado</RouterLink>

        <RouterLink v-if="!isLoggedIn" to="/modulo1" class="nav-btn" @click="menuOpen = false">Módulo 1</RouterLink>
        <RouterLink v-if="!isLoggedIn" to="/modulo2" class="nav-btn" @click="menuOpen = false">Módulo 2</RouterLink>
        <RouterLink v-if="!isLoggedIn" to="/modulo3" class="nav-btn" @click="menuOpen = false">Módulo 3</RouterLink>

        <RouterLink v-if="isLoggedIn" to="/AI" class="nav-btn btn-primary" @click="menuOpen = false">Aplicación</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin" class="nav-btn btn-secondary" @click="menuOpen = false">Admin</RouterLink>

        <RouterLink v-if="!isLoggedIn" to="/login" class="nav-btn btn-login" @click="menuOpen = false">Login</RouterLink>
        
        <template v-if="isLoggedIn">
          <button @click="handleLogout" class="logout-btn">
            <span>Logout</span>
            <span v-if="user?.name" class="user-chip">{{ user.name }}</span>
          </button>
          <RouterLink to="/profile" class="nav-btn" @click="menuOpen = false">Perfil</RouterLink>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { ref, onMounted, onUnmounted, watch } from "vue";
import { RouterLink } from "vue-router";
import { useAuth } from "../composables/use_auth.js";
import { useToast } from "vue-toastification";

const { isLoggedIn, user, isAdmin, logout } = useAuth();
const toast = useToast();
const menuOpen = ref(false);
const isDesktop = ref(window.matchMedia("(min-width: 1024px)").matches);

function updateIsDesktop() {
  isDesktop.value = window.matchMedia("(min-width: 1024px)").matches;
}

let logoutTimeout = null;
let logoutConfirmPending = false;
const handleLogout = async () => {
  if (logoutConfirmPending) {
    clearTimeout(logoutTimeout);
    logoutConfirmPending = false;
    await logout();
    toast.success("Sesión cerrada correctamente");
  } else {
    logoutConfirmPending = true;
    toast.warning("Haz clic otra vez para confirmar", {
      timeout: 4000,
      onClose: () => { logoutConfirmPending = false; }
    });
    logoutTimeout = setTimeout(() => { logoutConfirmPending = false; }, 4000);
  }
  menuOpen.value = false;
};

onMounted(() => {
  window.addEventListener("resize", updateIsDesktop);
});
onUnmounted(() => {
  window.removeEventListener("resize", updateIsDesktop);
});
watch(isDesktop, (val) => {
  if (val) menuOpen.value = false;
});
</script>

<style scoped>
/* --- Barra de Navegación Principal --- */
.navbar {
  width: 100%;
  height: 5rem; /* 80px */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  background: linear-gradient(90deg, rgba(185, 28, 28, 0.8), rgba(153, 27, 27, 0.8));
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(127, 29, 29, 0.5);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
}

/* --- Contenedor Interno (Centrado) --- */
.nav-container {
  width: 100%;
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* --- Contenedor de Enlaces Unificado --- */
.nav-links-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem; /* 12px */
}

/* --- Botones y Enlaces (Estilo Base) --- */
.nav-btn {
  min-width: 120px;
  padding: 0.6rem 1rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  cursor: pointer;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
  background-color: rgba(220, 38, 38, 0.4);
  border: 1px solid rgba(220, 38, 38, 0.6);
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.nav-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px -5px rgba(0,0,0,0.2), 0 4px 6px -4px rgba(0,0,0,0.15);
}

/* --- Botones de Colores (Sobrescriben el estilo base) --- */
.btn-primary { 
  background: linear-gradient(45deg, #2563eb, #3b82f6); 
  box-shadow: 0 0 15px -5px rgba(59, 130, 246, 0.8);
  border: none;
  color: white !important;
  text-shadow: none;
}
.btn-secondary { 
  background: linear-gradient(45deg, #16a34a, #10b981); 
  box-shadow: 0 0 15px -5px rgba(22, 163, 74, 0.8); 
  border: none;
  color: white !important;
  text-shadow: none;
}
.btn-login { 
  background: linear-gradient(45deg, #16a34a, #10b981); 
  box-shadow: 0 0 15px -5px rgba(22, 163, 74, 0.8);
  border: none;
  color: white !important;
  text-shadow: none;
}

/* --- Estado Activo del Enlace (Alto Contraste) --- */
.nav-btn.router-link-exact-active {
  background-color: #fff !important;
  color: #b91c1c !important;
  font-weight: 700;
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.8) !important;
  border-color: #fff;
  text-shadow: none;
}

/* --- Botón de Logout --- */
.logout-btn {
  min-width: 120px;
  padding: 0.6rem 1rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
  color: #fff !important;
  background-color: rgba(59, 130, 246, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.25s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  text-shadow: none;
}
.logout-btn:hover {
  background-color: rgba(59, 130, 246, 0.9);
  transform: scale(1.05);
  box-shadow: 0 8px 25px -5px rgba(0,0,0,0.2), 0 4px 6px -4px rgba(0,0,0,0.15);
}
.user-chip {
  background-color: rgba(0, 0, 0, 0.2);
  color: #fff;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}

/* --- Estilos para Móvil --- */
.hamburger-container { display: none; }
.hamburger-btn {
  color: #fff; font-size: 1.875rem; background: none; border: none;
  cursor: pointer; z-index: 60; text-shadow: 0 1px 3px rgba(0,0,0,0.4);
}

@media (max-width: 1279px) { /* xl breakpoint */
  .nav-container { justify-content: flex-end; }
  .hamburger-container { display: block; position: absolute; left: 1.5rem; }
  .nav-links-wrapper {
    display: none; position: fixed; top: 0; left: 0;
    width: 100%; height: 100vh;
    padding: 6rem 2rem 2rem 2rem;
    background: linear-gradient(135deg, rgba(185, 28, 28, 0.9), rgba(127, 29, 29, 0.95));
    backdrop-filter: blur(16px);
    flex-direction: column; align-items: center; justify-content: flex-start;
    gap: 1.5rem; opacity: 0;
    transform: translateY(-10px);
    transition: opacity 0.3s ease, transform 0.3s ease;
  }
  .nav-links-wrapper.open { display: flex; opacity: 1; transform: translateY(0); }
}
</style>
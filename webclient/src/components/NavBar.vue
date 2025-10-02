<template>
  <nav class="navbar">
    <div class="nav-container">
      <!-- Botón Hamburguesa -->
      <div class="hamburger-container">
        <button @click="menuOpen = !menuOpen" class="hamburger-btn" :class="{ 'is-active': menuOpen }" aria-label="Toggle menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <!-- Links -->
      <div class="nav-links-wrapper" :class="{ 'open': menuOpen }">
        <RouterLink to="/" class="nav-btn" @click="menuOpen = false">Inicio</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/about" class="nav-btn" @click="menuOpen = false">Proyecto</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/database" class="nav-btn" @click="menuOpen = false">Database</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/etiquetado" class="nav-btn" @click="menuOpen = false">Etiquetado</RouterLink>
        <RouterLink v-if="!isLoggedIn" to="/modulo1" class="nav-btn" @click="menuOpen = false">Preparación</RouterLink>
        <RouterLink v-if="!isLoggedIn" to="/modulo2" class="nav-btn" @click="menuOpen = false">Proceso</RouterLink>
        <RouterLink v-if="!isLoggedIn" to="/modulo3" class="nav-btn" @click="menuOpen = false">Aplicación</RouterLink>
        <RouterLink v-if="isLoggedIn" to="/AI" class="nav-btn btn-primary" @click="menuOpen = false">Aplicación</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin" class="nav-btn btn-secondary" @click="menuOpen = false">Admin</RouterLink>
        <RouterLink v-if="!isLoggedIn" to="/login" class="nav-btn btn-login" @click="menuOpen = false">Iniciar Sesión</RouterLink>
        <template v-if="isLoggedIn">
          <button @click="handleLogout" class="logout-btn">
            <span>Logout</span>
            <span v-if="user?.name" class="user-chip">{{ user.name }}</span>
          </button>
          <RouterLink to="/profile" class="nav-btn" @click="menuOpen = false">Perfil</RouterLink>
        </template>
      </div>
      
      <!-- Overlay -->
      <transition name="fade">
        <div v-if="menuOpen && !isDesktop" class="mobile-menu-overlay" @click="menuOpen = false"></div>
      </transition>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { RouterLink } from "vue-router";
import { useAuth } from "../composables/use_auth.js";
import { useToast } from "vue-toastification";

const { isLoggedIn, user, isAdmin, logout } = useAuth();
const toast = useToast();
const menuOpen = ref(false);
const isDesktop = ref(window.matchMedia("(min-width: 1280px)").matches);

function updateIsDesktop() {
  isDesktop.value = window.matchMedia("(min-width: 1280px)").matches;
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
watch(menuOpen, (isOpen) => {
  if (isOpen && !isDesktop.value) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});
</script>

<style scoped>
/* --- Barra de Navegación Principal --- */
.navbar {
  width: 100%;
  height: 5rem;
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
.nav-container {
  width: 100%;
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
}
.nav-links-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* --- Botones --- */
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
}

/* Botones especiales */
.btn-primary { 
  background: linear-gradient(45deg, #2563eb, #3b82f6); 
  border: none; color: white !important;
}
.btn-secondary { 
  background: linear-gradient(45deg, #16a34a, #10b981); 
  border: none; color: white !important;
}
.btn-login { 
  background: linear-gradient(45deg, #16a34a, #10b981); 
  border: none; color: white !important;
}
.nav-btn.router-link-exact-active {
  background-color: #fff !important;
  color: #b91c1c !important;
  font-weight: 700;
}

/* Logout */
.logout-btn {
  min-width: 120px;
  padding: 0.6rem 1rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
  color: #fff !important;
  background-color: rgba(59, 130, 246, 0.7);
  display: flex; align-items: center; justify-content: center;
  gap: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  cursor: pointer;
}
.logout-btn:hover { background-color: rgba(59, 130, 246, 0.9); }
.user-chip {
  background-color: rgba(0, 0, 0, 0.2);
  color: #fff; font-size: 0.75rem;
  padding: 0.25rem 0.5rem; border-radius: 9999px;
}

/* Hamburguesa */
.hamburger-container { display: none; }
.hamburger-btn {
  width: 30px; height: 24px; position: relative;
  background: none; border: none; cursor: pointer; z-index: 60;
}
.hamburger-btn span {
  display: block; position: absolute; height: 3px; width: 100%;
  background: #fff; border-radius: 3px; left: 0;
  transition: .25s ease-in-out;
}
.hamburger-btn span:nth-child(1) { top: 0; }
.hamburger-btn span:nth-child(2) { top: 10px; }
.hamburger-btn span:nth-child(3) { top: 20px; }
.hamburger-btn.is-active span:nth-child(1) { top: 10px; transform: rotate(135deg); }
.hamburger-btn.is-active span:nth-child(2) { opacity: 0; left: -30px; }
.hamburger-btn.is-active span:nth-child(3) { top: 10px; transform: rotate(-135deg); }

/* Overlay */
.mobile-menu-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(3px);
  z-index: 55;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* --- Estilos para móvil --- */
@media (max-width: 1279px) {
  .nav-container { justify-content: center; }
  .hamburger-container { display: block; position: absolute; left: 1.5rem; }

  .nav-links-wrapper {
    display: flex;
    position: fixed;
    top: 0;
    left: 0;
    width: 80%;
    max-width: 320px;
    height: 100vh;
    padding: 6rem 2rem 2rem 2rem;
    background: linear-gradient(135deg, rgb(185, 28, 28), rgb(127, 29, 29));
    flex-direction: column;
    align-items: flex-start;
    gap: 1.5rem;
    transform: translateX(-100%);
    opacity: 0;
    transition: transform 0.35s cubic-bezier(0.77, 0, 0.175, 1), opacity 0.3s ease;
    z-index: 58;
    box-shadow: 5px 0 30px rgba(0,0,0,0.3);
    overflow-y: auto;
  }
  .nav-links-wrapper.open {
    transform: translateX(0);
    opacity: 1;
  }
  .nav-links-wrapper::before {
    content: "NeuroBerry";
    font-size: 1.3rem;
    font-weight: bold;
    color: #fff;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.3);
    padding-bottom: 0.5rem;
    width: 100%;
    text-align: left;
  }
  .nav-links-wrapper .nav-btn,
  .nav-links-wrapper .logout-btn {
    width: 100%;
    padding: 1rem;
    font-size: 1.05rem;
    border-radius: 10px;
    background-color: #b91c1c;
    color: white;
    border: 1px solid rgba(255,255,255, 0.2);
    transition: background-color 0.25s, transform 0.25s;
  }
  .nav-links-wrapper .nav-btn:hover,
  .nav-links-wrapper .logout-btn:hover {
    background-color: #dc2626;
    transform: translateX(5px);
  }
  .nav-links-wrapper .nav-btn.router-link-exact-active {
    background-color: #fff !important;
    color: #b91c1c !important;
    border-color: #fff;
    font-weight: 700;
    transform: translateX(5px) scale(1.02);
  }
}
</style>
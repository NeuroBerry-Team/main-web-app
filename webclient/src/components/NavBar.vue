<template>
  <nav :class="['w-full flex items-center justify-between top-0 z-50 transition-all duration-500',
                scrolled ? 'bg-red-700/90 backdrop-blur-md shadow-md' : 'bg-transparent']">
    <!-- Hamburger -->
    <div class="flex-shrink-0 md:hidden">
      <button
        class="cursor-pointer p-1 text-white transition-transform duration-300 hover:scale-110"
        @click="menuOpen = !menuOpen"
        aria-label="Toggle menu"
      >
        <span class="text-3xl">☰</span>
      </button>
    </div>

    <!-- Menu (desktop inline, mobile dropdown) -->
    <transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0 -translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-4"
    >
      <div
          v-if="showMenu"
          :class="[
            !isDesktop
              ? 'flex absolute left-0 top-20 w-full z-40 py-4 flex-col items-center gap-4 bg-gradient-to-b from-[rgba(185,28,28,0.8)] via-[rgba(220,38,38,0.7)] to-[rgba(185,28,28,0.8)] rounded-xl shadow-lg'
              : 'hidden md:flex md:items-center md:gap-4 md:flex-row md:static md:bg-transparent'
          ]"
        >
        <RouterLink
          to="/"
          class="nav-btn"
          @click="menuOpen = false"
        >Inicio</RouterLink>
        <RouterLink
          to="/about"
          class="nav-btn"
          @click="menuOpen = false"
        >Proyecto</RouterLink>
        <RouterLink
          to="/database"
          class="nav-btn"
          @click="menuOpen = false"
        >Database</RouterLink>
        <RouterLink
          to="/etiquetado"
          class="nav-btn"
          @click="menuOpen = false"
        >Etiquetado</RouterLink>
        <RouterLink
          v-if="isLoggedIn"
          to="/AI"
          class="nav-btn bg-blue-600 text-white hover:bg-blue-700"
          @click="menuOpen = false"
        >Aplicación</RouterLink>
        <RouterLink
          v-if="isAdmin"
          to="/admin"
          class="nav-btn bg-purple-600 text-white hover:bg-purple-700"
          @click="menuOpen = false"
        >Admin</RouterLink>
      </div>
    </transition>

    <!-- Login / Logout -->
    <RouterLink
      v-if="!isLoggedIn"
      to="/login"
      class="nav-btn bg-green-600 text-white hover:bg-green-700"
      @click="menuOpen = false"
    >Login</RouterLink>

    <button
      v-if="isLoggedIn"
      @click="handleLogout"
      class="nav-btn bg-red-600 text-white hover:bg-red-700 flex items-center gap-2"
    >
      Logout
      <span v-if="user?.name" class="ml-1 text-xs bg-white/20 px-2 py-1 rounded">{{ user.name }}</span>
    </button>

    <!-- Profile -->
    <RouterLink
      v-if="isLoggedIn"
      to="/profile"
      class="nav-btn"
      @click="menuOpen = false"
    >Profile</RouterLink>

</nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { RouterLink } from "vue-router";
import { useAuth } from "../composables/use_auth.js";
import { useToast } from "vue-toastification";

const { isLoggedIn, user, isAdmin, logout } = useAuth();
const toast = useToast();
const menuOpen = ref(false);
const scrolled = ref(false);

// Detect desktop size
const isDesktop = ref(window.matchMedia("(min-width: 768px)").matches);

function updateIsDesktop() {
  isDesktop.value = window.matchMedia("(min-width: 768px)").matches;
}

function handleScroll() {
  scrolled.value = window.scrollY > 10;
}

const showMenu = computed(() => isDesktop.value || menuOpen.value);

let logoutTimeout = null;
let logoutConfirmPending = false;

const handleLogout = async () => {
  if (logoutConfirmPending) {
    // Second click - confirm logout
    clearTimeout(logoutTimeout);
    logoutConfirmPending = false;
    await logout();
    toast.success("Sesión cerrada correctamente");
  } else {
    // First click - show confirmation
    logoutConfirmPending = true;
    toast.warning("Haz clic en 'Cerrar Sesión' otra vez para confirmar", {
      timeout: 4000,
      onClose: () => {
        logoutConfirmPending = false;
      }
    });
    
    // Auto-cancel after 4 seconds
    logoutTimeout = setTimeout(() => {
      logoutConfirmPending = false;
    }, 4000);
  }
  menuOpen.value = false;
};

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
  window.addEventListener("resize", updateIsDesktop);
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
  window.removeEventListener("resize", updateIsDesktop);
});

// Close menu if switching to desktop
watch(isDesktop, (val) => {
  if (val) menuOpen.value = false;
});
</script>

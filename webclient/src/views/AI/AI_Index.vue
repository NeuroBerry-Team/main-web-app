<template>
  <div class="w-full min-h-screen max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 font-sans text-gray-800 flex flex-col gap-6 sm:gap-8 lg:gap-12 text-center">
    
    <!-- Logo - always visible -->
    <div class="flex justify-center mb-2 sm:mb-4 pt-8">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="max-w-xs sm:max-w-sm lg:max-w-md w-[90%] h-auto rounded-lg" />
    </div>

    <!-- Main index content - only visible when NOT on child routes -->
    <div v-if="!isOnChildRoute">
      <!-- Loading authentication -->
      <section v-if="authLoading" class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-slate-50 to-blue-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-4 sm:gap-6 lg:gap-8">
        <h1 class="text-xl sm:text-2xl lg:text-4xl font-extrabold text-red-700">Verificando autenticación...</h1>
      </section>

      <!-- Main content -->
      <div v-if="!authLoading" class="flex flex-col gap-6 sm:gap-8 lg:gap-12">
        <!-- Welcome section -->
        <section class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-slate-50 to-blue-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-4 sm:gap-6 lg:gap-8">
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-red-700">Centro de IA</h1>
          <p class="text-sm sm:text-base lg:text-lg leading-relaxed text-gray-600 px-2 sm:px-0">
            Bienvenido al centro de inteligencia artificial de NeuroBerry. Aquí puedes analizar imágenes de frambuesas y entrenar modelos de IA.
          </p>
          
          <!-- User status -->
          <div v-if="isLoggedIn && user?.role" class="inline-block break-words bg-green-50 px-3 py-2 sm:px-5 sm:py-3 rounded-lg text-green-700 font-medium text-xs sm:text-sm lg:text-base mt-2 lg:mt-4">
            Conectado como: <strong>{{ user.role }}</strong>
          </div>
          <div v-else-if="!isLoggedIn" class="inline-block bg-yellow-50 px-3 py-2 sm:px-5 sm:py-3 rounded-lg text-yellow-700 font-medium text-xs sm:text-sm lg:text-base mt-2 lg:mt-4">
            No has iniciado sesión
          </div>
        </section>

        <!-- Action buttons -->
        <section class="flex flex-col sm:flex-row gap-4 sm:gap-6 lg:gap-8 justify-center items-center">
          <!-- Train AI button - only for admins -->
          <router-link
            v-if="isAdmin"
            to="/AI/train"
            class="w-full sm:w-auto px-6 py-3 sm:px-8 sm:py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white text-sm sm:text-base lg:text-lg font-bold rounded-lg sm:rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center gap-2"
          >
            <span>🧠</span>
            <span>Entrenar IA</span>
          </router-link>
          
          <!-- Test AI button - for all logged in users -->
          <router-link
            v-if="isLoggedIn"
            to="/AI/inference"
            class="w-full sm:w-auto px-6 py-3 sm:px-8 sm:py-4 bg-gradient-to-r from-green-600 to-green-700 text-white text-sm sm:text-base lg:text-lg font-bold rounded-lg sm:rounded-xl hover:from-green-700 hover:to-green-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center gap-2"
          >
            <span>🔍</span>
            <span>Analizar Imagen</span>
          </router-link>
          
          <!-- Login button - for non-logged in users -->
          <router-link
            v-if="!isLoggedIn"
            to="/login"
            class="w-full sm:w-auto px-6 py-3 sm:px-8 sm:py-4 bg-gradient-to-r from-red-600 to-red-700 text-white text-sm sm:text-base lg:text-lg font-bold rounded-lg sm:rounded-xl hover:from-red-700 hover:to-red-800 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center justify-center gap-2"
          >
            <span>🔐</span>
            <span>Iniciar Sesión</span>
          </router-link>
        </section>

        <!-- Features info for non-logged users -->
        <section v-if="!isLoggedIn" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          <div class="p-4 sm:p-6 bg-white rounded-lg sm:rounded-xl shadow-md border border-gray-200">
            <div class="text-2xl sm:text-3xl mb-3 sm:mb-4">🔍</div>
            <h3 class="text-lg sm:text-xl font-bold text-gray-800 mb-2">Análisis de Imágenes</h3>
            <p class="text-sm sm:text-base text-gray-600">Analiza imágenes de frambuesas con nuestra IA avanzada para obtener información detallada.</p>
          </div>
          
          <div class="p-4 sm:p-6 bg-white rounded-lg sm:rounded-xl shadow-md border border-gray-200">
            <div class="text-2xl sm:text-3xl mb-3 sm:mb-4">🧠</div>
            <h3 class="text-lg sm:text-xl font-bold text-gray-800 mb-2">Entrenamiento IA</h3>
            <p class="text-sm sm:text-base text-gray-600">Funcionalidad avanzada para administradores para entrenar y mejorar los modelos de IA.</p>
          </div>
          
          <div class="p-4 sm:p-6 bg-white rounded-lg sm:rounded-xl shadow-md border border-gray-200 sm:col-span-2 lg:col-span-1">
            <div class="text-2xl sm:text-3xl mb-3 sm:mb-4">⚡</div>
            <h3 class="text-lg sm:text-xl font-bold text-gray-800 mb-2">Resultados Rápidos</h3>
            <p class="text-sm sm:text-base text-gray-600">Obtén análisis precisos y rápidos de tus imágenes en cuestión de segundos.</p>
          </div>
        </section>
      </div>
    </div>
    
    <!-- Router view for nested routes -->
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '../../composables/use_auth.js'

// Authentication
const { isLoggedIn, isAdmin, user, loading: authLoading, checkAuthStatus } = useAuth()

// Route handling
const route = useRoute()

// Check if we're on a child route (hide main content when on child routes)
const isOnChildRoute = computed(() => {
  return route.path !== '/AI'
})

// Check auth status on mount
onMounted(() => {
  checkAuthStatus()
})
</script>
<template>
  <div class="w-full min-h-screen max-w-6xl mx-auto p-4 sm:p-8 font-sans text-gray-800 flex flex-col gap-8 lg:gap-12" 
       style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">
    
    <!-- Logo Section -->
    <div class="flex justify-center mb-8">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" 
           class="max-w-xs w-full h-auto rounded-xl shadow-lg" />
    </div>

    <!-- Loading State -->
    <div v-if="authLoading" class="text-center py-16 bg-white rounded-2xl shadow-lg">
      <h1 class="text-3xl lg:text-4xl font-bold text-gray-700">Cargando perfil...</h1>
    </div>

    <!-- Main Profile Content -->
    <div v-else-if="isLoggedIn" class="flex flex-col gap-8 lg:gap-12">
      <!-- Welcome Section -->
      <section class="bg-gradient-to-br from-red-600 to-red-700 text-white p-6 sm:p-12 rounded-2xl shadow-xl text-center">
        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold mb-6 drop-shadow-lg">Mi Perfil</h1>
        <div class="flex flex-col items-center gap-4">
          <div class="mb-4">
            <span class="inline-block py-3 px-6 rounded-full font-semibold text-base uppercase tracking-wide shadow-lg"
                  :class="getRoleBadgeClass(user?.role)">
              {{ user?.role || 'Usuario' }}
            </span>
          </div>
          <p class="text-lg leading-relaxed max-w-2xl mx-auto opacity-95">
            Bienvenido al centro de control de tu cuenta NeuroBerry. 
            Desde aquí puedes acceder a todas las funciones disponibles y gestionar tu actividad.
          </p>
        </div>
      </section>

      <!-- Quick Actions Grid -->
      <section class="bg-white p-6 sm:p-12 rounded-2xl shadow-lg hover:-translate-y-1 transition-all duration-300">
        <div class="mb-8">
          <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800 text-center">
            Acceso Rápido
          </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 lg:gap-8">
          
          <!-- AI Analysis - Available to all logged users -->
          <router-link to="/AI/inference" 
                       class="group bg-white p-6 lg:p-8 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-t-4 border-green-500 no-underline">
            <div class="text-4xl lg:text-5xl mb-4">🔍</div>
            <h3 class="text-xl lg:text-2xl font-bold text-gray-800 mb-3">Analizar Imagen</h3>
            <p class="text-gray-600 leading-relaxed mb-6">
              Sube una imagen de frambuesa y obtén un análisis detallado de su estado de madurez
            </p>
            <div class="flex justify-between items-center">
              <span class="text-red-600 font-semibold group-hover:text-red-700 hover:underline">Ir al Análisis</span>
            </div>
          </router-link>

          <!-- AI Training - Only for admins -->
          <router-link 
            v-if="isAdmin" 
            to="/AI/train" 
            class="group bg-white p-6 lg:p-8 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-t-4 border-blue-500 no-underline"
          >
            <div class="text-4xl lg:text-5xl mb-4">🧠</div>
            <h3 class="text-xl lg:text-2xl font-bold text-gray-800 mb-3">Entrenar IA</h3>
            <p class="text-gray-600 leading-relaxed mb-6">
              Entrena y mejora los modelos de inteligencia artificial con nuevos datasets
            </p>
            <div class="flex justify-between items-center">
              <span class="text-red-600 font-semibold group-hover:text-red-700 hover:underline">Entrenar Modelo</span>
            </div>
          </router-link>

          <!-- Database Access - Only for admins -->
          <router-link v-if="isAdmin"
                to="/database" 
                class="group bg-white p-6 lg:p-8 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-t-4 border-amber-500 no-underline">
            <div class="text-4xl lg:text-5xl mb-4">📊</div>
            <h3 class="text-xl lg:text-2xl font-bold text-gray-800 mb-3">Base de Datos</h3>
            <p class="text-gray-600 leading-relaxed mb-6">
              Explora nuestra colección de 3000 imágenes organizadas en 5 clases de madurez
            </p>
            <div class="flex justify-between items-center">
            <span class="text-red-600 font-semibold group-hover:text-red-700 hover:underline">Ver Database</span>
            </div>
          </router-link>
        </div>
      </section>

      <!-- Profile Management -->
      <section class="bg-white p-6 sm:p-12 rounded-2xl shadow-lg hover:-translate-y-1 transition-all duration-300">
        <div class="mb-8">
          <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800 text-center">
            Gestión de Perfil
          </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
          
          <!-- Activity Summary -->
          <router-link to="/profile/activity" 
                       class="group bg-gradient-to-br from-gray-50 to-gray-100 p-6 lg:p-8 rounded-xl border border-gray-200 hover:bg-gradient-to-br hover:from-white hover:to-gray-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 no-underline">
            <div class="text-4xl lg:text-5xl mb-4">📈</div>
            <h3 class="text-xl lg:text-2xl font-bold text-gray-800 mb-3">Actividad</h3>
            <p class="text-gray-600 leading-relaxed mb-4">
              Revisa tu historial de análisis, métricas de uso y logs de actividad
            </p>
            <div class="text-sm text-gray-500 italic">
              <span>Análisis realizados, métricas y más</span>
            </div>
          </router-link>

          <!-- Settings -->
          <router-link to="/profile/settings" 
                       class="group bg-gradient-to-br from-gray-50 to-gray-100 p-6 lg:p-8 rounded-xl border border-gray-200 hover:bg-gradient-to-br hover:from-white hover:to-gray-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 no-underline">
            <div class="text-4xl lg:text-5xl mb-4">⚙️</div>
            <h3 class="text-xl lg:text-2xl font-bold text-gray-800 mb-3">Configuración</h3>
            <p class="text-gray-600 leading-relaxed mb-4">
              Modifica tu información personal, preferencias y configuración de la cuenta
            </p>
            <div class="text-sm text-gray-500 italic">
              <span>Personaliza tu experiencia</span>
            </div>
          </router-link>
        </div>
      </section>

      <!-- Feature Overview -->
      <section class="bg-white p-6 sm:p-12 rounded-2xl shadow-lg hover:-translate-y-1 transition-all duration-300">
        <div class="mb-8">
          <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800 text-center">
            ¿Qué puedes hacer en NeuroBerry?
          </h2>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div class="text-center p-6 lg:p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl hover:-translate-y-1 transition-transform duration-300">
            <div class="text-3xl lg:text-4xl mb-4">🎯</div>
            <h4 class="text-lg lg:text-xl font-semibold text-gray-800 mb-3">Análisis Preciso</h4>
            <p class="text-gray-600 leading-relaxed text-sm lg:text-base">
              Nuestro modelo de IA puede clasificar frambuesas en 5 estados diferentes de madurez con alta precisión
            </p>
          </div>

          <div class="text-center p-6 lg:p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl hover:-translate-y-1 transition-transform duration-300">
            <div class="text-3xl lg:text-4xl mb-4">⚡</div>
            <h4 class="text-lg lg:text-xl font-semibold text-gray-800 mb-3">Resultados Rápidos</h4>
            <p class="text-gray-600 leading-relaxed text-sm lg:text-base">
              Obtén análisis instantáneos de tus imágenes con tiempos de respuesta de segundos
            </p>
          </div>

          <div class="text-center p-6 lg:p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl hover:-translate-y-1 transition-transform duration-300">
            <div class="text-3xl lg:text-4xl mb-4">📱</div>
            <h4 class="text-lg lg:text-xl font-semibold text-gray-800 mb-3">Interfaz Amigable</h4>
            <p class="text-gray-600 leading-relaxed text-sm lg:text-base">
              Diseño intuitivo y responsivo que funciona perfectamente en cualquier dispositivo
            </p>
          </div>

          <div v-if="isAdmin" class="text-center p-6 lg:p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl hover:-translate-y-1 transition-transform duration-300">
            <div class="text-3xl lg:text-4xl mb-4">🔧</div>
            <h4 class="text-lg lg:text-xl font-semibold text-gray-800 mb-3">Herramientas Avanzadas</h4>
            <p class="text-gray-600 leading-relaxed text-sm lg:text-base">
              Como administrador, tienes acceso a herramientas de entrenamiento y gestión avanzada
            </p>
          </div>
        </div>
      </section>

      <!-- Admin Section -->
      <section v-if="isAdmin" class="bg-gradient-to-br from-yellow-400 to-orange-500 p-6 sm:p-12 rounded-2xl shadow-xl text-gray-900 hover:-translate-y-1 transition-all duration-300">
        <div class="mb-8">
          <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-center">
            Panel de Administración
          </h2>
          <div class="w-20 h-1 bg-gray-800 mx-auto mt-2 rounded"></div> <!-- Divider -->
        </div>
        <div class="bg-white bg-opacity-90 backdrop-blur-sm p-6 lg:p-8 rounded-xl">
          <div class="flex flex-col lg:flex-row items-center gap-6 lg:gap-8">
            <div class="text-4xl lg:text-5xl flex-shrink-0">🛡️</div>
            <div class="flex-1 text-center lg:text-left">
              <h3 class="text-xl lg:text-2xl font-bold text-gray-800 mb-2">Acceso de Administrador</h3>
              <p class="text-gray-600 leading-relaxed">
                Tienes permisos especiales para gestionar usuarios, entrenar modelos y acceder a funciones avanzadas.
              </p>
            </div>
            <router-link to="/admin" 
                         class="bg-gradient-to-r from-red-600 to-red-700 text-white py-3 px-6 rounded-xl font-semibold hover:-translate-y-1 hover:shadow-lg transition-all duration-300 whitespace-nowrap no-underline">
              Ir al Panel Admin
            </router-link>
          </div>
        </div>
      </section>
    </div>

    <!-- Not Logged In State -->
    <div v-else class="text-center py-16 bg-white rounded-2xl shadow-lg">
      <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-700 mb-4">Acceso Requerido</h1>
      <p class="text-lg lg:text-xl text-gray-600 my-8 leading-relaxed max-w-2xl mx-auto">
        Para acceder a tu perfil y utilizar las funciones de NeuroBerry, necesitas iniciar sesión.
      </p>
      <router-link to="/login" 
                   class="inline-block bg-gradient-to-r from-red-600 to-red-700 text-white py-3 px-8 rounded-xl font-semibold text-lg hover:-translate-y-1 hover:shadow-lg transition-all duration-300 no-underline">
        Iniciar Sesión
      </router-link>
    </div>

    <!-- Router view for nested routes -->
    <div class="mt-8">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuth } from '../../composables/use_auth.js'

// Authentication
const { isLoggedIn, user, loading: authLoading, checkAuthStatus, isAdmin } = useAuth()

// Methods
const getRoleBadgeClass = (role) => {
  switch(role) {
    case 'ADMIN':
    case 'SUPERADMIN':
      return 'bg-gradient-to-r from-yellow-400 to-orange-500 text-gray-900'
    case 'AI_USER':
      return 'bg-gradient-to-r from-blue-500 to-blue-700 text-white'
    default:
      return 'bg-gradient-to-r from-green-500 to-green-700 text-white'
  }
}

// Initialize
onMounted(() => {
  checkAuthStatus()
})
</script>
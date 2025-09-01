<template>
  <!-- Use Teleport to render modal outside of parent component -->
  <Teleport to="body">
    <div class="modal-overlay" @click.self="closeModal">
      <div class="modal-container" @click.stop>
        <div class="bg-gradient-to-r from-red-600 via-red-700 to-red-800 text-white p-6 flex items-center justify-between relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12"></div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <div class="text-2xl">📈</div>
            <h2 class="text-2xl font-bold">Actividad del Usuario</h2>
          </div>
          
          <button 
            @click="closeModal" 
            class="relative z-10 text-white hover:text-red-200 text-3xl font-light w-10 h-10 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-all duration-200 hover:rotate-90 transform"
            title="Cerrar ventana (ESC)"
          >
            ×
          </button>
        </div>

      <div class="p-8 overflow-y-auto max-h-[calc(85vh-100px)] bg-gray-50">
        <div class="space-y-8">
          
          <!-- Summary Cards -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-blue-500 hover:shadow-xl transition-shadow duration-300">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-600">Total Análisis</p>
                  <p class="text-2xl font-bold text-gray-900">47</p>
                </div>
                <div class="text-3xl text-blue-500">🔍</div>
              </div>
            </div>
            
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-green-500 hover:shadow-xl transition-shadow duration-300">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-600">Último Acceso</p>
                  <p class="text-2xl font-bold text-gray-900">Hoy</p>
                </div>
                <div class="text-3xl text-green-500">⏰</div>
              </div>
            </div>
            
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-purple-500 hover:shadow-xl transition-shadow duration-300">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-600">Precisión Promedio</p>
                  <p class="text-2xl font-bold text-gray-900">94.2%</p>
                </div>
                <div class="text-3xl text-purple-500">🎯</div>
              </div>
            </div>
          </div>

          <!-- Recent Analysis Section -->
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div class="flex items-center space-x-3 mb-6">
              <div class="text-2xl">📊</div>
              <h3 class="text-xl font-bold text-gray-800">Análisis Recientes</h3>
            </div>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors duration-200">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="text-green-600 font-semibold">🍓</span>
                  </div>
                  <div>
                    <p class="font-semibold text-gray-800">Frambuesa - Estado Maduro</p>
                    <p class="text-sm text-gray-600">Hace 2 horas • Confianza: 96%</p>
                  </div>
                </div>
                <div class="text-sm text-gray-500">14:30</div>
              </div>
              
              <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors duration-200">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
                    <span class="text-yellow-600 font-semibold">🍓</span>
                  </div>
                  <div>
                    <p class="font-semibold text-gray-800">Frambuesa - En Maduración</p>
                    <p class="text-sm text-gray-600">Hace 5 horas • Confianza: 89%</p>
                  </div>
                </div>
                <div class="text-sm text-gray-500">11:15</div>
              </div>
            </div>
            
            <div class="mt-6 pt-4 border-t border-gray-200">
              <router-link to="/profile/activity/inferences" 
                           class="inline-flex items-center text-red-600 hover:text-red-700 font-semibold transition-colors duration-200">
                Ver todos los análisis
                <span class="ml-2">→</span>
              </router-link>
            </div>
          </div>

          <!-- Usage Metrics Section -->
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div class="flex items-center space-x-3 mb-6">
              <div class="text-2xl">📈</div>
              <h3 class="text-xl font-bold text-gray-800">Métricas de Uso</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Análisis esta semana</span>
                  <span class="font-semibold text-gray-800">12</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Tiempo promedio por análisis</span>
                  <span class="font-semibold text-gray-800">2.3s</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Funciones más utilizadas</span>
                  <span class="font-semibold text-gray-800">Análisis IA</span>
                </div>
              </div>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Días activos este mes</span>
                  <span class="font-semibold text-gray-800">18</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Mejor racha de uso</span>
                  <span class="font-semibold text-gray-800">7 días</span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Imágenes procesadas</span>
                  <span class="font-semibold text-gray-800">47</span>
                </div>
              </div>
            </div>
            
            <div class="mt-6 pt-4 border-t border-gray-200">
              <router-link to="/profile/activity/metrics" 
                           class="inline-flex items-center text-red-600 hover:text-red-700 font-semibold transition-colors duration-200">
                Ver métricas detalladas
                <span class="ml-2">→</span>
              </router-link>
            </div>
          </div>

          <!-- Activity Logs Section -->
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div class="flex items-center space-x-3 mb-6">
              <div class="text-2xl">📝</div>
              <h3 class="text-xl font-bold text-gray-800">Registro de Actividad</h3>
            </div>
            <div class="space-y-3">
              <div class="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200">
                <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                <div class="flex-1">
                  <p class="text-sm text-gray-800">Inicio de sesión exitoso</p>
                  <p class="text-xs text-gray-500">Hoy a las 14:25</p>
                </div>
              </div>
              
              <div class="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200">
                <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div class="flex-1">
                  <p class="text-sm text-gray-800">Análisis de imagen completado</p>
                  <p class="text-xs text-gray-500">Hoy a las 14:30</p>
                </div>
              </div>
              
              <div class="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200">
                <div class="w-2 h-2 bg-purple-500 rounded-full"></div>
                <div class="flex-1">
                  <p class="text-sm text-gray-800">Acceso a perfil de usuario</p>
                  <p class="text-xs text-gray-500">Hoy a las 16:45</p>
                </div>
              </div>
            </div>
            
            <div class="mt-6 pt-4 border-t border-gray-200">
              <router-link to="/profile/activity/logs" 
                           class="inline-flex items-center text-red-600 hover:text-red-700 font-semibold transition-colors duration-200">
                Ver registro completo
                <span class="ml-2">→</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  </Teleport>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const closeModal = () => {
  router.back() // Go back to parent route
}

// Close modal on Escape key
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    closeModal()
  }
}

// Add event listener for Escape key
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  // Disable body scrolling when modal opens
  document.body.style.overflow = 'hidden'
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  // Re-enable body scrolling when modal closes
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style>
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background-color: rgba(0, 0, 0, 0.6) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 999999 !important;
  padding: 1rem !important;
}

.modal-container {
  background-color: white !important;
  border-radius: 1.5rem !important;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
  max-width: 80rem !important;
  width: 100% !important;
  max-height: 85vh !important;
  overflow: hidden !important;
  transform: scale(1) !important;
  transition: all 0.3s ease !important;
}

.modal-container:hover {
  transform: scale(1.01) !important;
}
</style>
<template>
  <!-- TODO: Finish metrics view -->
  <Teleport to="body">
    <div class="modal-overlay">
      <div class="modal-container">
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 p-4 rounded-t-3xl">
          <div class="flex justify-between items-center">
            <div>
              <h2 class="text-2xl font-bold text-white">Métricas Detalladas</h2>
              <p class="text-purple-100 mt-1">Análisis avanzado de rendimiento</p>
            </div>
            <button @click="$router.push('/profile')" class="text-white hover:text-gray-200 focus:outline-none">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="flex-1 p-8 overflow-y-auto">
          <div class="text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
              <svg class="w-8 h-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
            <h3 class="text-2xl font-bold text-gray-800 mb-2">Métricas Avanzadas</h3>
            <p class="text-gray-600 mb-8">Esta sección estará disponible próximamente con análisis detallados de rendimiento y estadísticas avanzadas.</p>
            
            <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6">
              <h4 class="text-lg font-semibold text-gray-800 mb-2">Próximamente incluirá:</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                <div class="flex items-center space-x-2">
                  <div class="w-2 h-2 bg-purple-400 rounded-full"></div>
                  <span class="text-gray-600">Métricas de precisión</span>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="w-2 h-2 bg-pink-400 rounded-full"></div>
                  <span class="text-gray-600">Análisis temporal</span>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="w-2 h-2 bg-purple-400 rounded-full"></div>
                  <span class="text-gray-600">Patrones de uso</span>
                </div>
                <div class="flex items-center space-x-2">
                  <div class="w-2 h-2 bg-pink-400 rounded-full"></div>
                  <span class="text-gray-600">Comparativas</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'ProfileActivityMetrics'
}
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
  max-width: 90rem !important;
  width: 95% !important;
  max-height: 95vh !important;
  overflow: hidden !important;
  transform: scale(1) !important;
  transition: all 0.3s ease !important;
  display: flex !important;
  flex-direction: column !important;
}

.modal-container:hover {
  transform: scale(1.01) !important;
}
</style>

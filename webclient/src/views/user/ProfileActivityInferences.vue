<template>
  <!-- Gallery Modal -->
  <Teleport to="body" v-if="!selectedInference">
    <div class="modal-overlay" @click.self="goBack">
      <div class="modal-container" @click.stop>
        <div class="bg-gradient-to-r from-red-600 via-red-700 to-red-800 text-white p-6 flex items-center justify-between relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12"></div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <div class="text-2xl">📊</div>
            <h2 class="text-2xl font-bold">Galería de Análisis</h2>
          </div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <router-link 
              to="/AI/inference"
              class="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors duration-200 text-sm"
            >
              Nuevo análisis
            </router-link>
            <button 
              @click="goBack" 
              class="text-white hover:text-red-200 text-3xl font-light w-10 h-10 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-all duration-200 hover:rotate-90 transform"
              title="Cerrar ventana (ESC)"
            >
              ×
            </button>
          </div>
        </div>

        <div class="flex-1 p-8 overflow-y-auto bg-gray-50">
          <!-- Gallery Content -->
          <div class="space-y-6">
            <div v-if="loading" class="text-center py-12">
              <div class="text-4xl mb-4">⏳</div>
              <p class="text-gray-500">Cargando galería...</p>
            </div>
            
            <div v-else-if="error" class="text-center py-12">
              <div class="text-4xl mb-4">❌</div>
              <p class="text-red-500 mb-4">Error al cargar los análisis</p>
              <button 
                @click="loadInferences"
                class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Intentar de nuevo
              </button>
            </div>
            
            <div v-else-if="!inferences.length" class="text-center py-12">
              <div class="text-6xl mb-6">📊</div>
              <h3 class="text-xl font-semibold text-gray-700 mb-2">No tienes análisis aún</h3>
              <p class="text-gray-500 mb-6">Comienza analizando tu primera imagen de frambuesa</p>
              <router-link 
                to="/AI/inference"
                class="inline-flex items-center px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Crear primer análisis
                <span class="ml-2">→</span>
              </router-link>
            </div>
            
            <!-- Gallery Grid -->
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              <div
                v-for="inference in inferences"
                :key="inference.id"
                @click="openInferenceDetail(inference)"
                class="group cursor-pointer bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden"
              >
                <!-- Image Thumbnail -->
                <div class="aspect-square bg-gray-100 relative overflow-hidden">
                  <img 
                    v-if="inference.baseImageUrl"
                    :src="inference.baseImageUrl"
                    :alt="inference.result"
                    class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    @error="handleImageError"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                    <span class="text-3xl">🍓</span>
                  </div>
                  
                  <!-- Overlay with confidence -->
                   <!-- TODO: Implement confidence this is just placeholder -->
                  <div v-if="inference.confidence" class="absolute top-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded-full">
                    {{ Math.round(inference.confidence * 100) }}%
                  </div>
                  
                  <!-- Analysis result overlay -->
                  <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-3">
                    <p class="text-white text-sm font-medium truncate">{{ inference.result }}</p>
                  </div>
                </div>
                
                <!-- Info Section -->
                <div class="p-3">
                  <div class="flex justify-between items-center text-xs text-gray-500">
                    <span>{{ formatActivityTime(inference.createdOn) }}</span>
                    <span class="font-mono">#{{ inference.id }}</span>
                  </div>
                  <div class="text-xs text-gray-400 mt-1">
                    {{ formatTime(inference.createdOn) }}
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Load More Button -->
            <div v-if="hasMore && !loading" class="text-center mt-8">
              <button
                @click="loadMoreInferences"
                class="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors duration-200"
              >
                Cargar más análisis
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Individual Inference Detail Modal -->
  <Teleport to="body" v-if="selectedInference">
    <div class="modal-overlay" @click.self="closeInferenceDetail">
      <div class="modal-container" style="max-width: 80rem;" @click.stop>
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 p-6 flex items-center justify-between relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12"></div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <div class="text-2xl">🔍</div>
            <div>
              <h2 class="text-2xl font-bold text-white">Detalle del Análisis</h2>
              <p class="text-purple-100 mt-1">Información completa del análisis realizado</p>
            </div>
          </div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <button
              @click="backToGallery"
              class="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors duration-200 text-sm"
            >
              ← Volver a la galería
            </button>
            <button 
              @click="closeInferenceDetail"
              class="text-white hover:text-purple-200 text-3xl font-light w-10 h-10 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-all duration-200 hover:rotate-90 transform"
              title="Cerrar ventana (ESC)"
            >
              ×
            </button>
          </div>
        </div>
        
        <div class="flex-1 p-6 overflow-y-auto bg-gray-50">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Images Section -->
            <div class="space-y-4">
              <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Imagen Original</h3>
                <div class="bg-gray-100 rounded-lg p-4">
                  <img 
                    v-if="selectedInference.baseImageUrl"
                    :src="selectedInference.baseImageUrl"
                    :alt="selectedInference.name || 'Imagen original'"
                    class="w-full h-64 object-cover rounded-lg"
                    @error="handleImageError"
                  />
                  <div v-else class="w-full h-64 flex items-center justify-center text-gray-500">
                    <span>Imagen no disponible</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Resultado del Análisis</h3>
                <div class="bg-gray-100 rounded-lg p-4">
                  <img 
                    v-if="selectedInference.generatedImageUrl"
                    :src="selectedInference.generatedImageUrl"
                    :alt="'Análisis: ' + selectedInference.result"
                    class="w-full h-64 object-cover rounded-lg"
                    @error="handleImageError"
                  />
                  <div v-else class="w-full h-64 flex items-center justify-center text-gray-500">
                    <span>Resultado no disponible</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Details Section -->
            <div class="space-y-6">
              <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Información del Análisis</h3>
                <div class="space-y-4">
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">ID del Análisis</span>
                    <span class="font-mono text-sm text-gray-800">#{{ selectedInference.id }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Resultado</span>
                    <span class="font-semibold text-gray-800">{{ selectedInference.result }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Fecha de Análisis</span>
                    <span class="text-gray-800">{{ formatDate(selectedInference.createdOn) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Hora</span>
                    <span class="text-gray-800">{{ formatTime(selectedInference.createdOn) }}</span>
                  </div>
                  <div v-if="selectedInference.confidence" class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Confianza</span>
                    <span class="font-semibold text-green-600">{{ Math.round(selectedInference.confidence * 100) }}%</span>
                  </div>
                  <div v-if="selectedInference.name" class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Nombre</span>
                    <span class="text-gray-800">{{ selectedInference.name }}</span>
                  </div>
                </div>
              </div>
              
              <div class="pt-4">
                <button
                  @click="downloadResults"
                  class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                >
                  Descargar Resultados
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const inferences = ref([])
const selectedInference = ref(null)
const loading = ref(true)
const error = ref(null)
const hasMore = ref(false)
const currentPage = ref(1)

const goBack = () => {
  router.push('/profile') // Always return to the main profile page
}

// Close modal on Escape key
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    if (selectedInference.value) {
      closeInferenceDetail()
    } else {
      goBack()
    }
  }
}

// Add and remove keyboard event listeners
onMounted(async () => {
  document.addEventListener('keydown', handleKeydown)
  await loadInferences()
  
  // Check if there's an inference ID in the URL after loading
  const inferenceId = route.query.id
  if (inferenceId && inferences.value.length > 0) {
    const inference = inferences.value.find(i => i.id == inferenceId)
    if (inference) {
      selectedInference.value = inference
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

const formatActivityTime = (timestamp) => {
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMinutes / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffMinutes < 1) return 'Ahora mismo'
    if (diffMinutes < 60) return `Hace ${diffMinutes}m`
    if (diffHours < 24) return `Hace ${diffHours}h`
    if (diffDays === 1) return 'Ayer'
    if (diffDays < 7) return `Hace ${diffDays} días`
    
    return date.toLocaleDateString('es-ES')
  } catch (error) {
    return 'Fecha inválida'
  }
}

const formatDate = (timestamp) => {
  try {
    return new Date(timestamp).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch (error) {
    return 'Fecha inválida'
  }
}

const formatTime = (timestamp) => {
  try {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return 'Hora inválida'
  }
}

const loadInferences = async (page = 1) => {
  try {
    loading.value = true
    error.value = null
    
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    const response = await fetch(`${apiUrl}/users/inferences?page=${page}&limit=20`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    
    if (data.success && data.inferences) {
      if (page === 1) {
        inferences.value = data.inferences
      } else {
        inferences.value = [...inferences.value, ...data.inferences]
      }
      hasMore.value = data.pagination?.has_next || false
    } else {
      throw new Error(data.error || 'Failed to fetch inferences')
    }
  } catch (err) {
    console.error('Error fetching inferences:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const loadMoreInferences = async () => {
  if (loading.value || !hasMore.value) return
  
  currentPage.value += 1
  await loadInferences(currentPage.value)
}

const openInferenceDetail = (inference) => {
  selectedInference.value = inference
  // Update URL to include inference ID
  router.replace({ query: { ...route.query, id: inference.id } })
}

const closeInferenceDetail = () => {
  selectedInference.value = null
  // Remove ID from URL and go back to profile
  router.push('/profile')
}

const backToGallery = () => {
  selectedInference.value = null
  // Remove ID from URL but stay in gallery
  const { id, ...queryWithoutId } = route.query
  router.replace({ query: queryWithoutId })
}

const downloadResults = () => {
  // TODO: Implement download functionality
  console.log('Download results for inference:', selectedInference.value.id)
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  event.target.parentNode.innerHTML = '<div class="w-full h-64 flex items-center justify-center text-gray-500">Imagen no disponible</div>'
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

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
                v-for="inference in inferencesWithConfidence"
                :key="inference.id"
                @click="openInferenceDetail(inference)"
                class="gallery-item group cursor-pointer bg-white rounded-xl shadow-md overflow-hidden"
              >
                <!-- Image Thumbnail -->
                                <!-- Image Thumbnail -->
                <div class="aspect-square bg-gray-100 relative overflow-hidden">
                  <img 
                    v-if="inference.baseImageUrl"
                    :src="getCachedImageUrl(inference.baseImageUrl)"
                    :alt="inference.result"
                    class="w-full h-full object-cover transition-opacity duration-300"
                    @error="handleImageError"
                    @load="onImageLoad(inference)"
                    loading="lazy"
                    decoding="async"
                  />
                  
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                    <span class="text-3xl">🍓</span>
                  </div>
                  
                  <!-- Overlay with confidence -->
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
                    loading="lazy"
                  />
                  <div v-else class="w-full h-64 flex items-center justify-center text-gray-500">
                    <span>Imagen no disponible</span>
                  </div>
                </div>
              </div>
              
              <div>
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-lg font-semibold text-gray-700">Resultado del Análisis</h3>
                  
                  <!-- Box Controls Toggle -->
                  <button
                    @click="toggleBoxControls"
                    :class="['flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm', 
                             showBoxControls ? 'bg-purple-100 text-purple-700 border border-purple-300' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
                  >
                    <span>{{ showBoxControls ? '🔧' : '📦' }}</span>
                    <span>{{ showBoxControls ? 'Ocultar controles' : 'Gestionar cajas' }}</span>
                  </button>
                </div>
                
                <!-- Box Controls Panel (Collapsible) -->
                <div v-if="showBoxControls" class="mb-4 bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                  <div class="flex items-center justify-between mb-3">
                    <h4 class="text-sm font-medium text-gray-700">Control de Detecciones</h4>
                    <div class="flex items-center space-x-2 text-xs text-gray-500">
                      <button
                        @click="toggleAllBoxes(true)"
                        class="px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                      >
                        Mostrar todas
                      </button>
                      <button
                        @click="toggleAllBoxes(false)"
                        class="px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                      >
                        Ocultar todas
                      </button>
                    </div>
                  </div>
                  
                  <!-- Individual Box Controls -->
                  <div class="space-y-2 max-h-32 overflow-y-auto">
                    <div
                      v-for="(box, index) in detectedBoxes"
                      :key="`box-${index}`"
                      :class="[
                        'flex items-center justify-between py-2 px-3 rounded-lg transition-all duration-200 cursor-pointer',
                        selectedBox === box 
                          ? 'bg-purple-100 border-2 border-purple-300 ring-1 ring-purple-200' 
                          : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                      ]"
                      @click="selectBox(box)"
                    >
                      <div class="flex items-center space-x-3">
                        <!-- Color indicator -->
                        <div 
                          :class="[
                            'w-3 h-3 rounded-full border transition-all duration-200',
                            selectedBox === box 
                              ? 'border-purple-400 ring-2 ring-purple-200' 
                              : 'border-gray-300'
                          ]"
                          :style="{ backgroundColor: box.color }"
                        ></div>
                        
                        <!-- Box info -->
                        <div>
                          <span 
                            :class="[
                              'text-sm font-medium transition-colors duration-200',
                              selectedBox === box ? 'text-purple-800' : 'text-gray-700'
                            ]"
                          >
                            {{ box.label }}
                          </span>
                          <span 
                            :class="[
                              'text-xs ml-2 transition-colors duration-200',
                              selectedBox === box ? 'text-purple-600' : 'text-gray-500'
                            ]"
                          >
                            {{ Math.round(box.confidence * 100) }}%
                          </span>
                        </div>
                      </div>
                      
                      <!-- Toggle switch -->
                      <label class="relative inline-flex items-center cursor-pointer" @click.stop>
                        <input 
                          type="checkbox" 
                          v-model="box.visible" 
                          class="sr-only peer"
                          @change="updateImageWithBoxes"
                        >
                        <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-500"></div>
                      </label>
                    </div>
                  </div>
                </div>
                
                <div class="bg-gray-100 rounded-lg p-4 relative">
                  <div class="relative">
                    <!-- Hidden image for canvas processing -->
                    <img 
                      v-if="selectedInference.generatedImageUrl"
                      ref="hiddenImage"
                      :src="currentResultImage"
                      :alt="showBoxControls ? 'Imagen original para control manual' : 'Análisis: ' + selectedInference.result"
                      class="hidden"
                      @load="onImageLoad"
                      @error="handleImageError"
                    />
                    
                    <!-- Canvas for drawing boxes -->
                    <canvas 
                      v-if="selectedInference.generatedImageUrl && showBoxControls"
                      ref="imageCanvas"
                      class="w-full h-64 object-cover rounded-lg transition-all duration-300 border border-gray-200 cursor-pointer"
                      @click="handleCanvasClick"
                      @dblclick="handleCanvasDoubleClick"
                    ></canvas>
                    
                    <!-- Regular image when not in box control mode -->
                    <img 
                      v-else-if="selectedInference.generatedImageUrl"
                      :src="currentResultImage"
                      :alt="'Análisis: ' + selectedInference.result"
                      class="w-full h-64 object-cover rounded-lg transition-all duration-300"
                      @error="handleImageError"
                    />
                    
                    <div v-else class="w-full h-64 flex items-center justify-center text-gray-500">
                      <span>Resultado no disponible</span>
                    </div>
                    
                    <!-- Image mode indicator -->
                    <div 
                      v-if="showBoxControls" 
                      class="absolute top-2 left-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full shadow-sm"
                    >
                      📐 Modo edición
                    </div>
                    
                    <!-- Box count indicator -->
                    <div 
                      v-if="showBoxControls && detectedBoxes.length > 0"
                      class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full shadow-sm"
                    >
                      {{ detectedBoxes.filter(box => box.visible).length }}/{{ detectedBoxes.length }} cajas
                    </div>
                    
                    <!-- Selected box indicator -->
                    <div 
                      v-if="showBoxControls && selectedBox"
                      class="absolute bottom-2 left-2 bg-purple-600 text-white text-xs px-3 py-1 rounded-full shadow-sm flex items-center space-x-1"
                    >
                      <div 
                        class="w-2 h-2 rounded-full"
                        :style="{ backgroundColor: selectedBox.color }"
                      ></div>
                      <span>{{ selectedBox.label }} seleccionado</span>
                    </div>
                    
                    <!-- Instructions -->
                    <div 
                      v-if="showBoxControls && detectedBoxes.length > 0"
                      class="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded shadow-sm"
                    >
                      Click: seleccionar • Doble-click: mostrar/ocultar
                    </div>
                    
                    <!-- Loading overlay -->
                    <div v-if="imageLoading" class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                      <div class="text-white text-center">
                        <div class="animate-spin text-2xl mb-2">⚙️</div>
                        <p class="text-sm">Actualizando vista...</p>
                      </div>
                    </div>
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
                  <div v-if="confidenceCache.get(selectedInference.id)" class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Confianza Promedio</span>
                    <span class="font-semibold text-green-600">{{ Math.round(confidenceCache.get(selectedInference.id) * 100) }}%</span>
                  </div>
                  <div v-if="selectedInference.name" class="flex justify-between items-center py-2 border-b border-gray-200">
                    <span class="text-gray-600">Nombre</span>
                    <span class="text-gray-800">{{ selectedInference.name }}</span>
                  </div>
                  <!-- Class Count Section -->
                  <div v-if="selectedInference" class="py-2 border-b border-gray-200">
                    <div class="flex flex-col space-y-2">
                      <span class="text-gray-600">Conteo por Clase:</span>
                      
                      <!-- Loading state -->
                      <div v-if="!metadataLoaded.has(selectedInference.id)" class="pl-4 flex items-center space-x-2 text-sm text-gray-500">
                        <div class="animate-spin text-xs">⚙️</div>
                        <span>Calculando conteos...</span>
                      </div>
                      
                      <!-- Class counts -->
                      <div v-else-if="classCountSummary && Object.keys(classCountSummary).length > 0" class="pl-4 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                        <div v-for="(count, className) in classCountSummary" :key="className" 
                            class="flex justify-between bg-gray-50 px-3 py-1 rounded">
                          <span class="text-gray-700">{{ className }}:</span>
                          <span class="font-medium text-gray-900">{{ count }}</span>
                        </div>
                      </div>
                      
                      <!-- Show all classes with 0 count when no detections -->
                      <div v-else class="pl-4 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                        <div v-for="(label, classId) in getAllClassLabels()" :key="classId" 
                            class="flex justify-between bg-gray-50 px-3 py-1 rounded">
                          <span class="text-gray-700">{{ label }}:</span>
                          <span class="font-medium text-gray-900">0</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- Model Information Section -->
                  <div class="py-2 border-b border-gray-200">
                    <div class="flex justify-between items-center">
                      <span class="text-gray-600">Modelo</span>
                      <div class="flex items-center space-x-2">
                        <span class="text-gray-800">
                          {{ selectedInference.modelId ? `#${selectedInference.modelId}` : (selectedInference.model || 'N/A') }}
                        </span>
                        <button
                          @click="toggleModelDetails"
                          :class="[
                            'text-xs px-2 py-1 rounded transition-colors duration-200',
                            showModelDetails ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          ]"
                          :disabled="!selectedInference.modelId"
                        >
                          {{ showModelDetails ? 'Ocultar' : 'Detalles' }}
                        </button>
                      </div>
                    </div>
                    
                    <!-- Expanded Model Details -->
                    <div v-if="showModelDetails" class="mt-3 pl-4 border-l-2 border-blue-200 bg-blue-50 rounded-r-lg p-3">
                      <div v-if="getModelDetails(selectedInference.modelId)" class="space-y-2 text-sm">
                        <div class="flex justify-between">
                          <span class="text-blue-600 font-medium">Nombre:</span>
                          <span class="text-blue-800">{{ getModelDetails(selectedInference.modelId).name }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-blue-600 font-medium">Versión:</span>
                          <span class="text-blue-800">{{ getModelDetails(selectedInference.modelId).version }}</span>
                        </div>
                        <div class="flex justify-between">
                          <span class="text-blue-600 font-medium">Tipo:</span>
                          <span class="text-blue-800">{{ getModelDetails(selectedInference.modelId).modelType }}</span>
                        </div>
                        <div v-if="getModelDetails(selectedInference.modelId).description" class="pt-2 border-t border-blue-200">
                          <span class="text-blue-600 font-medium">Descripción:</span>
                          <p class="text-blue-800 mt-1 text-xs leading-relaxed">{{ getModelDetails(selectedInference.modelId).description }}</p>
                        </div>
                        <div class="flex justify-between text-xs text-blue-500 pt-2 border-t border-blue-200">
                          <span>Creado:</span>
                          <span>{{ formatDate(getModelDetails(selectedInference.modelId).createdOn) }}</span>
                        </div>
                      </div>
                      
                      <!-- Loading state -->
                      <div v-else-if="selectedInference.modelId" class="flex items-center justify-center py-4">
                        <div class="animate-spin text-blue-500 mr-2">⚙️</div>
                        <span class="text-blue-600 text-sm">Cargando detalles del modelo...</span>
                      </div>
                      
                      <!-- No model ID available -->
                      <div v-else class="text-blue-600 text-sm py-2">
                        <span>ℹ️ ID del modelo no disponible</span>
                      </div>
                    </div>
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
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const inferences = ref([])
const selectedInference = ref(null)
const loading = ref(true)
const error = ref(null)
const hasMore = ref(false)
const currentPage = ref(1)

// Box controls variables
const showBoxControls = ref(false)
const imageLoading = ref(false)
const detectedBoxes = ref([])
const selectedBox = ref(null) // Track which box is currently selected/highlighted

// Confidence calculation cache
const confidenceCache = ref(new Map())
const metadataLoaded = ref(new Set()) // Track which inferences have loaded metadata

// Computed property to get confidence values efficiently
const inferencesWithConfidence = computed(() => {
  return inferences.value.map(inference => ({
    ...inference,
    confidence: confidenceCache.value.get(inference.id) || null
  }))
})

// Model details cache and toggle state
const modelDetailsCache = ref(new Map())
const showModelDetails = ref(false)

// Canvas refs and variables
const imageCanvas = ref(null)
const hiddenImage = ref(null)
const canvasContext = ref(null)

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
  window.addEventListener('resize', handleResize)
  await loadInferences()
  
  // Check if there's an inference ID in the URL after loading
  const inferenceId = route.query.id
  if (inferenceId && inferences.value.length > 0) {
    const inference = inferences.value.find(i => i.id == inferenceId)
    if (inference) {
      await openInferenceDetail(inference)
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('resize', handleResize)
  
  // Clear preloaded images set
  preloadedImages.value.clear()
  
  // Clear metadata loaded tracking
  metadataLoaded.value.clear()
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
      
      // Preload images after a short delay to avoid conflicts with initial render
      nextTick(() => {
        setTimeout(() => {
          preloadGalleryImages()
        }, 500)
      })
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

const openInferenceDetail = async (inference) => {
  selectedInference.value = inference
  // Reset detected boxes - they will be populated from metadata
  detectedBoxes.value = []
  // Reset model details toggle state
  showModelDetails.value = false
  // Update URL to include inference ID
  router.replace({ query: { ...route.query, id: inference.id } })

  // Always fetch metadata when opening inference detail
  console.log('Opening inference detail for:', inference.id)
  await fetchBoxMetadataFromMinio(inference.id)
}

const closeInferenceDetail = () => {
  selectedInference.value = null
  showModelDetails.value = false
  // Reset box control state
  showBoxControls.value = false
  detectedBoxes.value = []
  selectedBox.value = null
  // Remove ID from URL and go back to profile
  router.push('/profile')
}

const backToGallery = () => {
  selectedInference.value = null
  showModelDetails.value = false
  // Reset box control state
  showBoxControls.value = false
  detectedBoxes.value = []
  selectedBox.value = null
  // Remove ID from URL but stay in gallery
  const { id, ...queryWithoutId } = route.query
  router.replace({ query: queryWithoutId })
}

const downloadResults = () => {
  // TODO: Implement download functionality
  console.log('Download results for inference:', selectedInference.value.id)
}

// Computed property for the current image with selected boxes
const currentResultImage = computed(() => {
  if (!selectedInference.value) return null
  
  // If controls are hidden, show the normal results image with boxes already drawn
  if (!showBoxControls.value) {
    return selectedInference.value.generatedImageUrl
  }
  
  // If controls are visible, show the original image (without boxes)
  // so we can draw boxes manually on canvas using metadata from Minio
  return selectedInference.value.baseImageUrl
})

const toggleAllBoxes = (visible) => {
  detectedBoxes.value.forEach(box => {
    box.visible = visible
  })
  updateImageWithBoxes()
}

const selectBox = (box) => {
  selectedBox.value = box
  
  // Redraw canvas to show selection highlighting
  if (showBoxControls.value) {
    updateImageWithBoxes()
  }
}

// Calculate and cache average confidence from metadata
const calculateAverageConfidence = (inferenceId, detections) => {
  if (!detections || detections.length === 0) {
    confidenceCache.value.set(inferenceId, null)
    return null
  }
  
  // Calculate average confidence from all detections
  const totalConfidence = detections.reduce((sum, detection) => sum + detection.confidence, 0)
  const averageConfidence = totalConfidence / detections.length
  
  // Cache the result
  confidenceCache.value.set(inferenceId, averageConfidence)
  
  return averageConfidence
}

// Image caching functions
const preloadedImages = ref(new Set()) // Track which images have been preloaded

const getCachedImageUrl = (originalUrl) => {
  // For now, just return the original URL and let CSS handle the resizing
  // This is not ideal but avoids the double download issue
  // TODO: Implement server-side thumbnail generation
  return originalUrl
}

const getFullSizeImageUrl = (originalUrl) => {
  // For detail views, return the original URL
  return originalUrl
}

const preloadImage = async (imageUrl) => {
  if (!imageUrl || preloadedImages.value.has(imageUrl)) {
    return
  }

  try {
    // Create a hidden image element to trigger browser caching
    const img = new Image()
    img.crossOrigin = 'use-credentials'
    
    await new Promise((resolve, reject) => {
      img.onload = () => {
        preloadedImages.value.add(imageUrl)
        resolve()
      }
      img.onerror = reject
      img.src = imageUrl
    })
  } catch (error) {
    console.warn('Failed to preload image:', imageUrl, error)
  }
}

const preloadGalleryImages = async () => {
  // Preload first few images to improve performance
  const visibleInferences = inferences.value.slice(0, 10)
  
  for (const inference of visibleInferences) {
    if (inference.baseImageUrl) {
      try {
        await preloadImage(inference.baseImageUrl)
        // Small delay between each image
        await new Promise(resolve => setTimeout(resolve, 100))
      } catch (error) {
        console.warn('Failed to preload image:', inference.baseImageUrl, error)
      }
    }
  }
}

// Model details functions
const getModelDetails = (modelId) => {
  if (!modelId) return null
  
  // Check if we have it cached
  if (modelDetailsCache.value.has(modelId)) {
    return modelDetailsCache.value.get(modelId)
  }
  
  // Return null for now, will be loaded when requested
  return null
}

const fetchModelDetails = async (modelId) => {
  if (!modelId || modelDetailsCache.value.has(modelId)) {
    return modelDetailsCache.value.get(modelId)
  }
  
  try {
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    const response = await fetch(`${apiUrl}/models/`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.success && data.models) {
        // Cache all models for future use
        data.models.forEach(model => {
          modelDetailsCache.value.set(model.id, {
            id: model.id,
            name: model.name,
            version: model.version,
            description: model.description,
            modelType: model.modelType,
            createdOn: model.createdOn,
            updatedOn: model.updatedOn
          })
        })
        
        return modelDetailsCache.value.get(modelId)
      }
    }
  } catch (error) {
    console.error('Error fetching model details:', error)
    // Cache null to avoid repeated failed requests
    modelDetailsCache.value.set(modelId, null)
  }
  
  return null
}

const toggleModelDetails = async () => {
  showModelDetails.value = !showModelDetails.value
  
  // Load model details if showing and not already loaded
  if (showModelDetails.value && selectedInference.value?.modelId) {
    await fetchModelDetails(selectedInference.value.modelId)
  }
}

const toggleBoxControls = async () => {
  imageLoading.value = true
  
  try {
    // Add a small delay to show the loading state during image transition
    await new Promise(resolve => setTimeout(resolve, 300))
    
    showBoxControls.value = !showBoxControls.value
    
    // If we're entering box control mode and don't have metadata, fetch it
    if (showBoxControls.value) {
      if (!metadataLoaded.value.has(selectedInference.value.id)) {
        console.log('Loading metadata for box controls...')
        await fetchBoxMetadataFromMinio(selectedInference.value.id)
      }
      
      // Try to setup canvas after metadata is loaded
      nextTick(() => {
        if (imageCanvas.value && hiddenImage.value && detectedBoxes.value.length > 0) {
          setupCanvas()
          drawImageWithBoxes()
        }
      })
    } else {
      // Clear selection when exiting edit mode but keep detectedBoxes for class counts
      selectedBox.value = null
      if (canvasContext.value) {
        canvasContext.value.clearRect(0, 0, imageCanvas.value.width, imageCanvas.value.height)
      }
    }
  } catch (error) {
    console.error('Error toggling box controls:', error)
  } finally {
    imageLoading.value = false
  }
}

const fetchBoxMetadataFromMinio = async (inferenceId) => {
  try {
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    const response = await fetch(`${apiUrl}/inferences/getInferenceMetadata/${inferenceId}`, {
      method: 'GET',
      credentials: 'include'
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.success && data.metadata) {
      // Mark metadata as loaded
      metadataLoaded.value.add(inferenceId)
      
      // Calculate and cache average confidence
      calculateAverageConfidence(inferenceId, data.metadata.detections)
      
      // Only update detectedBoxes if not already populated (prevent double processing)
      if (detectedBoxes.value.length === 0) {
        // Get original image dimensions from metadata
        const imageInfo = data.metadata.image_info
        const originalImageSize = imageInfo ? imageInfo.original_size : null
        
        console.log('Metadata loaded:', {
          inferenceId,
          detectionsCount: data.metadata.detections.length,
          imageInfo,
          originalImageSize,
          fullMetadata: data.metadata
        })
        
        // Map the detections to detectedBoxes format
        detectedBoxes.value = data.metadata.detections.map((detection, index) => {
          let bbox_normalized = null
          
          // Calculate normalized coordinates using original image dimensions
          if (detection.bbox && originalImageSize) {
            const [originalHeight, originalWidth] = originalImageSize
            bbox_normalized = normalizeCoordinates(detection.bbox, [originalWidth, originalHeight])
            
            // Validate normalization was successful
            if (!bbox_normalized) {
              console.error(`Failed to normalize coordinates for box ${index}:`, detection.bbox)
            }
          } else {
            console.warn(`Box ${index} missing bbox or image size:`, {
              hasBbox: !!detection.bbox,
              hasImageSize: !!originalImageSize,
              bbox: detection.bbox,
              imageSize: originalImageSize,
              detection: detection
            })
          }
          
          return {
            id: index, // Use index as unique ID
            label: getClassLabel(detection.class_id),
            confidence: detection.confidence,
            visible: true, // All boxes visible by default
            color: getBoxColor(detection.class_id),
            bbox: detection.bbox, // Original pixel coordinates (for reference)
            bbox_normalized: bbox_normalized, // Properly normalized coordinates (0-1 range)
            center_point: detection.center_point,
            area: detection.area,
            class_id: detection.class_id
          }
        })
        
        console.log('Created detectedBoxes:', detectedBoxes.value.length)
      }
      
      // Try to draw boxes if canvas is ready and box controls are active
      nextTick(() => {
        if (showBoxControls.value && imageCanvas.value && hiddenImage.value) {
          setupCanvas()
          drawImageWithBoxes()
        }
      })
    } else {
      console.error('Failed to load metadata:', data.error || 'Unknown error')
      // Mark as loaded even on failure to stop loading state
      metadataLoaded.value.add(inferenceId)
    }
  } catch (error) {
    console.error('Error fetching metadata from Minio:', error)
    // Mark as loaded even on error to stop loading state
    metadataLoaded.value.add(inferenceId)
  }
}

/**
 * Normalize bounding box coordinates to 0-1 range for resolution-independent storage
 * 
 * @param {Object|Array} bbox - Bounding box coordinates (either {x1,y1,x2,y2} object or [x1,y1,x2,y2] array)
 * @param {Array} imageSize - [width, height] of the original image in pixels
 * @returns {Object|null} Normalized coordinates {x1,y1,x2,y2} in 0-1 range, or null if invalid
 * 
 * The normalized coordinate system ensures that:
 * - All coordinates are between 0 and 1
 * - x1,y1 represents the top-left corner
 * - x2,y2 represents the bottom-right corner
 * - x1 <= x2 and y1 <= y2 (enforced by this function)
 * - Coordinates can be scaled to any canvas/display size by multiplying by target dimensions
 */
const normalizeCoordinates = (bbox, imageSize) => {
  const [imageWidth, imageHeight] = imageSize
  
  // Handle both array format [x1, y1, x2, y2] and object format {x1, y1, x2, y2}
  let x1, y1, x2, y2;
  
  if (Array.isArray(bbox)) {
    [x1, y1, x2, y2] = bbox;
  } else if (bbox && typeof bbox === 'object') {
    ({ x1, y1, x2, y2 } = bbox);
  } else {
    console.error('Invalid bbox format:', bbox);
    return null;
  }
  
  // Normalize coordinates to 0-1 range
  const normalized = {
    x1: Math.max(0, Math.min(1, x1 / imageWidth)),
    y1: Math.max(0, Math.min(1, y1 / imageHeight)),
    x2: Math.max(0, Math.min(1, x2 / imageWidth)),
    y2: Math.max(0, Math.min(1, y2 / imageHeight))
  };
  
  // Ensure x1 <= x2 and y1 <= y2 for consistent box drawing
  return {
    x1: Math.min(normalized.x1, normalized.x2),
    y1: Math.min(normalized.y1, normalized.y2),
    x2: Math.max(normalized.x1, normalized.x2),
    y2: Math.max(normalized.y1, normalized.y2)
  };
}

const classCountSummary = computed(() => {
  if (!detectedBoxes.value || !selectedInference.value || !metadataLoaded.value.has(selectedInference.value.id)) {
    return null
  }
  
  // Initialize all classes with 0
  const allClasses = getAllClassLabels()
  const counts = {}
  
  // Initialize all classes with 0
  Object.values(allClasses).forEach(label => {
    counts[label] = 0
  })
  
  // Count detected boxes by their actual labels
  detectedBoxes.value.forEach(box => {
    const label = box.label || getClassLabel(box.class_id)
    if (label && counts.hasOwnProperty(label)) {
      counts[label] += 1
    }
  })
  
  return counts
})

const getAllClassLabels = () => {
  return {
    0: 'C5 DarkRed',
    1: 'C4 BrightRed', 
    2: 'C3 Orange (Red dot)',
    3: 'C2 Green',
    4: 'C1 Boton'
  }
}

const getClassLabel = (classId) => {
  const classLabels = {
    0: 'C5 DarkRed',
    1: 'C4 BrightRed',
    2: 'C3 Orange (Red dot)',
    3: 'C2 Green',
    4: 'C1 Boton',
  }
  return classLabels[classId] || `Clase ${classId}`
}

const getBoxColor = (classId) => {
  const classColors = {
    0: '#991B1B', // C5 DarkRed
    1: '#EF4444', // C4 BrightRed
    2: '#F59E0B', // C3 Orange
    3: '#22C55E', // C2 Green
    4: '#6B7280', // C1 Boton (gray)
  }
  return classColors[classId] || '#6366F1' // Default purple color
}

const updateImageWithBoxes = () => {
  if (showBoxControls.value && canvasContext.value) {
    drawImageWithBoxes()
  }
  
  const visibleBoxes = detectedBoxes.value.filter(box => box.visible)
}

// Canvas setup and drawing functions
const onImageLoad = (inference) => {
  console.log('Image loaded. showBoxControls:', showBoxControls.value, 'canvas:', !!imageCanvas.value, 'hiddenImage:', !!hiddenImage.value, 'detectedBoxes count:', detectedBoxes.value.length)
  
  // Handle canvas setup for box drawing
  if (showBoxControls.value && imageCanvas.value && hiddenImage.value && detectedBoxes.value.length > 0) {
    nextTick(() => {
      setupCanvas()
      drawImageWithBoxes()
    })
  }
}

const setupCanvas = () => {
  if (!imageCanvas.value || !hiddenImage.value) {
    console.warn('Canvas setup failed: missing canvas or image', {
      canvas: !!imageCanvas.value,
      image: !!hiddenImage.value
    })
    return
  }
  
  const canvas = imageCanvas.value
  const img = hiddenImage.value
  const ctx = canvas.getContext('2d')
  canvasContext.value = ctx
  
  // Set canvas size to match the display size
  const containerWidth = canvas.parentElement.clientWidth
  const containerHeight = 256 // h-64 class = 256px
  
  canvas.width = containerWidth
  canvas.height = containerHeight
  
  // Configure canvas context
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
}

const drawImageWithBoxes = () => {
  if (!canvasContext.value || !hiddenImage.value) {
    console.warn('Cannot draw: missing context or image', {
      context: !!canvasContext.value,
      image: !!hiddenImage.value
    })
    return
  }
  
  // Validate coordinate system before drawing (only show warnings for real issues)
  const coordinateIssues = validateCoordinateSystem()
  
  const ctx = canvasContext.value
  const canvas = imageCanvas.value
  const img = hiddenImage.value
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Draw the image
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
  
  // Draw visible bounding boxes, but save the selected box for last (to render on top)
  const visibleBoxes = detectedBoxes.value.filter(box => box.visible)
  const nonSelectedBoxes = visibleBoxes.filter(box => box !== selectedBox.value)
  const selectedBoxToDrawLast = visibleBoxes.find(box => box === selectedBox.value)
  
  // Draw all non-selected boxes first
  nonSelectedBoxes.forEach((box, index) => {
    drawBoundingBox(ctx, box)
  })
  
  // Draw selected box last (on top of everything)
  if (selectedBoxToDrawLast) {
    drawBoundingBox(ctx, selectedBoxToDrawLast)
  }
}

const drawBoundingBox = (ctx, box) => {
  const { bbox_normalized, color, label, confidence } = box
  
  if (!bbox_normalized || typeof bbox_normalized !== 'object') {
    console.warn('Missing or invalid normalized coordinates for box:', box.label, bbox_normalized)
    return
  }
  
  // Validate normalized coordinates are in 0-1 range
  const { x1, y1, x2, y2 } = bbox_normalized
  if (x1 < 0 || x1 > 1 || y1 < 0 || y1 > 1 || x2 < 0 || x2 > 1 || y2 < 0 || y2 > 1) {
    console.warn('Normalized coordinates out of range (0-1):', bbox_normalized, 'for box:', box.label)
  }
  
  // Get canvas dimensions
  const canvas = imageCanvas.value
  const canvasWidth = canvas.width
  const canvasHeight = canvas.height
  
  // Convert normalized coordinates (0-1) to canvas pixels
  const pixelX1 = Math.round(x1 * canvasWidth)
  const pixelY1 = Math.round(y1 * canvasHeight)
  const pixelX2 = Math.round(x2 * canvasWidth)
  const pixelY2 = Math.round(y2 * canvasHeight)
  
  // Calculate rectangle position and dimensions (ensuring positive dimensions)
  const x = Math.min(pixelX1, pixelX2)
  const y = Math.min(pixelY1, pixelY2)
  const width = Math.abs(pixelX2 - pixelX1)
  const height = Math.abs(pixelY2 - pixelY1)
  
  // Ensure we have valid dimensions
  if (width <= 0 || height <= 0) {
    console.warn('Invalid box dimensions:', { width, height, box: box.label, normalized: bbox_normalized })
    return
  }
  
  // Check if this box is selected for highlighting
  const isSelected = selectedBox.value === box
  
  // Draw box outline with highlighting
  ctx.strokeStyle = color
  ctx.lineWidth = isSelected ? 4 : 2  // Thicker line for selected box
  ctx.setLineDash(isSelected ? [5, 5] : [])  // Dashed line for selected box
  ctx.strokeRect(x, y, width, height)
  
  // Draw highlight background for selected box
  if (isSelected) {
    ctx.fillStyle = color + '20'  // Semi-transparent background
    ctx.fillRect(x, y, width, height)
    
    // Draw outer glow effect
    ctx.shadowColor = color
    ctx.shadowBlur = 10
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.setLineDash([])
    ctx.strokeRect(x - 2, y - 2, width + 4, height + 4)
    
    // Reset shadow
    ctx.shadowColor = 'transparent'
    ctx.shadowBlur = 0
  }
  
  // Draw filled background for label
  const labelText = `${label} ${Math.round(confidence * 100)}%`
  ctx.font = isSelected ? 'bold 12px Inter, system-ui, sans-serif' : '12px Inter, system-ui, sans-serif'
  const textMetrics = ctx.measureText(labelText)
  const labelWidth = textMetrics.width + 8
  const labelHeight = 20
  
  // Position label above the box, but inside if near top edge
  const labelY = y > labelHeight ? y - labelHeight : y + labelHeight
  
  // Use brighter color for selected box label
  ctx.fillStyle = isSelected ? '#7C3AED' : color  // Purple for selected, original color otherwise
  ctx.fillRect(x, labelY, labelWidth, labelHeight)
  
  // Draw label text
  ctx.fillStyle = 'white'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillText(labelText, x + 4, labelY + labelHeight / 2)
}

const handleCanvasClick = (event) => {
  if (!showBoxControls.value || !canvasContext.value) return
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // Find clicked box
  const clickedBox = findBoxAtPosition(x, y)
  if (clickedBox) {
    // Select the clicked box (or deselect if already selected)
    selectBox(clickedBox === selectedBox.value ? null : clickedBox)
  } else {
    // Clicked on empty area, deselect any selected box
    selectBox(null)
  }
}

const handleCanvasDoubleClick = (event) => {
  if (!showBoxControls.value || !canvasContext.value) return
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // Find double-clicked box
  const clickedBox = findBoxAtPosition(x, y)
  if (clickedBox) {
    // Toggle box visibility on double-click
    clickedBox.visible = !clickedBox.visible
    // Force reactivity update for the controls list
    detectedBoxes.value = [...detectedBoxes.value]
    updateImageWithBoxes()
  }
}

const findBoxAtPosition = (x, y) => {
  const canvas = imageCanvas.value
  const canvasWidth = canvas.width
  const canvasHeight = canvas.height
  
  // Check boxes in reverse order (last drawn on top)
  for (let i = detectedBoxes.value.length - 1; i >= 0; i--) {
    const box = detectedBoxes.value[i]
    if (!box.visible || !box.bbox_normalized) continue
    
    // Convert normalized coordinates to canvas pixels (same logic as drawBoundingBox)
    const pixelX1 = Math.round(box.bbox_normalized.x1 * canvasWidth)
    const pixelY1 = Math.round(box.bbox_normalized.y1 * canvasHeight)
    const pixelX2 = Math.round(box.bbox_normalized.x2 * canvasWidth)
    const pixelY2 = Math.round(box.bbox_normalized.y2 * canvasHeight)
    
    // Calculate rectangle bounds (ensuring positive dimensions)
    const boxX = Math.min(pixelX1, pixelX2)
    const boxY = Math.min(pixelY1, pixelY2)
    const boxWidth = Math.abs(pixelX2 - pixelX1)
    const boxHeight = Math.abs(pixelY2 - pixelY1)
    
    if (x >= boxX && x <= boxX + boxWidth && y >= boxY && y <= boxY + boxHeight) {
      return box
    }
  }
  return null
}

// Utility function to validate coordinate system integrity
const validateCoordinateSystem = () => {
  const issues = []
  
  detectedBoxes.value.forEach((box, index) => {
    if (!box.bbox_normalized) {
      issues.push(`Box ${index} (${box.label}): Missing normalized coordinates`)
      return
    }
    
    const { x1, y1, x2, y2 } = box.bbox_normalized
    
    // Check if coordinates are in valid 0-1 range
    if (x1 < 0 || x1 > 1 || y1 < 0 || y1 > 1 || x2 < 0 || x2 > 1 || y2 < 0 || y2 > 1) {
      issues.push(`Box ${index} (${box.label}): Coordinates out of 0-1 range: ${JSON.stringify(box.bbox_normalized)}`)
    }
    
    // Check if box has positive dimensions
    if (Math.abs(x2 - x1) <= 0 || Math.abs(y2 - y1) <= 0) {
      issues.push(`Box ${index} (${box.label}): Invalid dimensions: ${JSON.stringify(box.bbox_normalized)}`)
    }
  })
  
  if (issues.length > 0) {
    console.warn('Coordinate system validation failed:', issues.length, 'issues found')
    return issues
  }
  
  return issues
}

// Window resize handler to adjust canvas
const handleResize = () => {
  if (showBoxControls.value && imageCanvas.value) {
    nextTick(() => {
      setupCanvas()
      drawImageWithBoxes()
    })
  }
}

const handleImageError = (event) => {
  event.target.src = '/frambuesas_1.jpg' // Fallback image
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

.gallery-item {
  transition: box-shadow 0.2s ease !important;
  will-change: box-shadow !important;
}

.gallery-item:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
  transform: translateY(-2px) !important;
}

.gallery-item img {
  transition: transform 0.2s ease !important;
  will-change: transform !important;
}

.gallery-item:hover img {
  transform: scale(1.05) !important;
}
</style>

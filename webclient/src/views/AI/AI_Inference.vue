<template>
  <div class="w-full min-h-screen max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 font-sans text-gray-800 flex flex-col gap-6 sm:gap-8 lg:gap-12 text-center">
    <!-- Authentication check -->
    <section v-if="!isLoggedIn && !authLoading" class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-slate-50 to-blue-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-4 sm:gap-6 lg:gap-8">
      <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-red-700">Acceso Requerido</h1>
      <p class="text-sm sm:text-base lg:text-lg leading-relaxed text-gray-600 px-2">
        Debes iniciar sesión para acceder a la herramienta de análisis de imágenes.
      </p>
      <router-link to="/login" class="inline-block px-4 py-2 sm:px-6 sm:py-3 bg-red-700 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-red-800 transition-all duration-300">Iniciar Sesión</router-link>
    </section>

    <!-- Loading authentication -->
    <section v-if="authLoading" class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-slate-50 to-blue-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-4 sm:gap-6 lg:gap-8">
      <h1 class="text-xl sm:text-2xl lg:text-4xl font-extrabold text-red-700">Verificando autenticación...</h1>
    </section>

    <!-- Main content - only show if authenticated -->
    <div v-if="isLoggedIn" class="flex flex-col gap-6 sm:gap-8 lg:gap-12">
      <section class="flex flex-col gap-4 sm:gap-6 lg:gap-8">
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-red-700">Análisis de Imágenes</h1>
        <p class="text-sm sm:text-base lg:text-lg leading-relaxed text-gray-600 px-2 sm:px-0">
          Carga una imagen de frambuesa para iniciar el proceso de análisis con nuestra IA.
        </p>
        <p v-if="user?.name" class="inline-block break-words bg-green-50 px-3 py-2 sm:px-5 sm:py-3 rounded-lg text-green-700 font-medium text-xs sm:text-sm lg:text-base mt-2 lg:mt-4">
          Conectado como: <strong>{{ user.name }} {{ user.lastName }}</strong>
        </p>
      </section>

      <section class="flex flex-col items-center gap-4 sm:gap-6">
        <!-- Model selection -->
        <div class="w-full max-w-sm sm:max-w-lg lg:max-w-2xl">
          <label for="model-select" class="block text-sm font-medium text-gray-700 mb-2">
            Selecciona el modelo de IA:
          </label>
          <select 
            id="model-select"
            v-model="selectedModel"
            :disabled="loading || modelsLoading || models.length === 0"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="" disabled>
              {{ modelsLoading ? 'Cargando modelos...' : models.length === 0 ? 'No hay modelos disponibles' : 'Selecciona un modelo' }}
            </option>
            <option 
              v-for="model in models" 
              :key="model.id" 
              :value="model.id"
            >
              {{ model.label }}
            </option>
          </select>
          <p v-if="modelsError" class="mt-1 text-xs text-red-600">
            Error cargando modelos: {{ modelsError }}
          </p>
          <p v-else-if="!modelsLoading && models.length === 0" class="mt-1 text-xs text-gray-500">
            No hay modelos disponibles. Contacta al administrador.
          </p>
          <p v-else-if="selectedModel && models.find(m => m.id === selectedModel)" class="mt-1 text-xs text-gray-600">
            Modelo seleccionado: {{ models.find(m => m.id === selectedModel)?.description || 'Sin descripción' }}
          </p>
        </div>

        <div class="w-full max-w-sm sm:max-w-lg lg:max-w-2xl border-2 sm:border-4 border-dashed border-red-700 rounded-xl sm:rounded-2xl bg-red-50/20 cursor-pointer flex justify-center items-center transition-all duration-300 hover:border-red-900 hover:bg-red-50/50 hover:scale-105 relative p-8 sm:p-10 lg:p-12" 
             @click="triggerFileInput" 
             :class="{ 
               'opacity-60 cursor-not-allowed hover:scale-100': loading, 
               'min-h-[240px] sm:min-h-[280px] lg:min-h-[320px]': !previewImage,
               'h-64 sm:h-80 lg:h-96': previewImage 
             }">
          <input
            type="file"
            ref="fileInput"
            accept="image/*"
            @change="onFileChange"
            style="display: none"
          />
          <div v-if="!previewImage" class="text-center text-gray-700 flex flex-col items-center justify-center w-full h-full">
            <div class="text-3xl sm:text-4xl lg:text-5xl mb-4 sm:mb-6">📁</div>
            <div class="flex flex-col items-center gap-2 sm:gap-3 max-w-[90%]">
              <span class="text-sm sm:text-base lg:text-lg font-medium text-red-700 leading-relaxed text-center">Haz clic aquí o arrastra una imagen para cargarla</span>
              <small class="text-gray-500 text-xs sm:text-sm leading-relaxed text-center">Formatos soportados: JPG, PNG, WebP</small>
            </div>
          </div>
          <img
            v-else
            :src="previewImage"
            alt="Vista previa"
            class="max-w-full max-h-full rounded-lg object-contain shadow-lg"
          />
        </div>

        <div v-if="previewImage" class="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full max-w-md">
          <button 
            class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-green-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-green-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed" 
            :disabled="loading || !selectedModel" 
            @click="startInference"
          >
            {{ loading ? 'Analizando...' : 'Iniciar análisis' }}
          </button>
          <button class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-red-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-red-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed" 
                  @click="resetImage" 
                  :disabled="loading">
            Cambiar imagen
          </button>
        </div>
      </section>
      
      <!-- Error message -->
      <section v-if="error || modelsError" class="bg-red-50 border-2 border-red-300 rounded-lg sm:rounded-xl p-4 sm:p-6 lg:p-8 text-center flex flex-col gap-4 sm:gap-6 lg:gap-8">
        <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-red-800">Error:</h2>
        <p v-if="error" class="text-red-700 font-medium text-sm sm:text-base mb-2 sm:mb-4 px-2">{{ error }}</p>
        <p v-if="modelsError" class="text-red-700 font-medium text-sm sm:text-base mb-2 sm:mb-4 px-2">Error de modelos: {{ modelsError }}</p>
        <button v-if="error?.includes('login') || modelsError?.includes('Authentication')" 
                @click="$router.push('/login')" 
                class="inline-block px-4 py-2 sm:px-6 sm:py-3 bg-red-700 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-red-800 transition-all duration-300">
          Ir al Login
        </button>
      </section>
      
      <!-- Results section -->
      <section v-if="result" class="bg-gradient-to-br from-green-50 to-emerald-100 border-2 border-green-300 rounded-lg sm:rounded-xl lg:rounded-2xl p-6 lg:p-8 text-center flex flex-col gap-6 shadow-xl">
        <h2 class="text-xl lg:text-2xl font-bold text-green-800">Resultado del Análisis</h2>
        
        <!-- Main image container - much larger and eye-friendly -->
        <div class="relative bg-white rounded-xl shadow-lg p-4">
          <!-- Loading overlay -->
          <div v-if="metadataLoading" class="absolute inset-0 bg-white/90 rounded-xl flex items-center justify-center z-20">
            <div class="flex flex-col items-center gap-3">
              <div class="w-10 h-10 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div>
              <p class="text-sm text-green-700 font-medium">Cargando análisis...</p>
            </div>
          </div>
          
          <!-- Main control buttons - sticky note style in top-right corner -->
          <div class="absolute top-4 right-4 z-10 flex flex-col gap-2">
            <button 
              @click="toggleBoxControls"
              :disabled="metadataLoading || !detectedBoxes.length"
              class="px-3 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1 shadow-lg"
              title="Alternar controles de cajas"
            >
              <span v-if="!showBoxControls">🔍</span>
              <span v-else>👁️</span>
              <span class="hidden sm:inline">{{ showBoxControls ? 'Ver' : 'Cajas' }}</span>
            </button>
            <button 
              @click="startNewAnalysis"
              class="px-3 py-2 bg-green-600 text-white text-xs font-bold rounded-lg hover:bg-green-700 transition-all duration-300 flex items-center justify-center gap-1 shadow-lg"
              title="Nuevo análisis"
            >
              🔄
              <span class="hidden sm:inline">Nuevo</span>
            </button>
          </div>
          
          <!-- Collapsible control panel - top left overlay -->
          <div v-if="showBoxControls && detectedBoxes.length > 0" class="absolute top-4 left-4 z-10">
            <div class="bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 transition-all duration-300"
                 :class="controlPanelExpanded ? 'w-80' : 'w-12'">
              
              <!-- Panel toggle button -->
              <button 
                @click="controlPanelExpanded = !controlPanelExpanded"
                class="w-full p-3 flex items-center justify-center hover:bg-gray-50 rounded-lg transition-colors"
                title="Alternar panel de controles"
              >
                <svg class="w-5 h-5 text-gray-600 transition-transform duration-300" 
                     :class="{ 'rotate-180': controlPanelExpanded }"
                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 5l7 7-7 7"></path>
                </svg>
              </button>
              
              <!-- Panel content -->
              <div v-if="controlPanelExpanded" class="p-4 border-t border-gray-100">
                <!-- Quick actions -->
                <div class="flex gap-2 mb-4">
                  <button 
                    @click="toggleAllBoxes(true)"
                    class="flex-1 px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                  >
                    ✓ Todas
                  </button>
                  <button 
                    @click="toggleAllBoxes(false)"
                    class="flex-1 px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                  >
                    ✗ Ninguna
                  </button>
                </div>
                
                <!-- Box list -->
                <div class="space-y-2 max-h-60 overflow-y-auto">
                  <div 
                    v-for="box in detectedBoxes" 
                    :key="box.id"
                    class="flex items-center gap-2 p-2 rounded border text-xs hover:bg-gray-50 transition-colors"
                    :class="{
                      'bg-blue-50 border-blue-300': selectedBox === box,
                      'bg-white border-gray-200': selectedBox !== box
                    }"
                    @click="selectBox(box)"
                  >
                    <input 
                      type="checkbox" 
                      v-model="box.visible"
                      @change="updateImageWithBoxes"
                      @click.stop
                      class="w-3 h-3"
                    />
                    <div 
                      class="w-3 h-3 rounded-sm border border-gray-400 flex-shrink-0"
                      :style="{ backgroundColor: box.color }"
                    ></div>
                    <div class="flex-1 min-w-0">
                      <div class="font-medium truncate" :style="{ color: box.color }">
                        {{ box.label }}
                      </div>
                      <div class="text-gray-500 text-xs">
                        {{ Math.round(box.confidence * 100) }}% confianza
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Help text -->
                <p class="text-xs text-gray-500 text-center mt-3 pt-3 border-t border-gray-100">
                  Clic = seleccionar, Checkbox = mostrar/ocultar
                </p>
                
                <!-- Magnifying glass controls -->
                <div class="mt-4 pt-3 border-t border-gray-100">
                  <div class="flex justify-center mb-3">
                    <button 
                      @click="toggleMagnifyingGlass"
                      :class="[
                        'px-4 py-2 text-white text-xs font-bold rounded-lg transition-all duration-300 flex items-center justify-center gap-1',
                        magnifyingGlassActive 
                          ? 'bg-purple-600 hover:bg-purple-700' 
                          : 'bg-indigo-600 hover:bg-indigo-700'
                      ]"
                    >
                      🔍 {{ magnifyingGlassActive ? 'Desactivar' : 'Activar' }}
                    </button>
                  </div>
                  
                  <!-- Magnifying glass settings -->
                  <div v-if="magnifyingGlassActive" class="space-y-3">
                    <!-- Zoom controls -->
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-medium text-gray-700">Zoom:</span>
                      <div class="flex items-center gap-1">
                        <button 
                          @click="magnifyingGlassZoom = Math.max(1.0, magnifyingGlassZoom - 0.2)"
                          class="px-2 py-1 bg-gray-600 text-white text-xs font-bold rounded hover:bg-gray-700 transition-all duration-300"
                          :disabled="magnifyingGlassZoom <= 1.0"
                          title="Reducir zoom"
                        >
                          -
                        </button>
                        <span class="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded min-w-[45px] text-center">
                          {{ magnifyingGlassZoom.toFixed(1) }}x
                        </span>
                        <button 
                          @click="magnifyingGlassZoom = Math.min(6.0, magnifyingGlassZoom + 0.2)"
                          class="px-2 py-1 bg-gray-600 text-white text-xs font-bold rounded hover:bg-gray-700 transition-all duration-300"
                          :disabled="magnifyingGlassZoom >= 6.0"
                          title="Aumentar zoom"
                        >
                          +
                        </button>
                      </div>
                    </div>
                    
                    <!-- Size controls -->
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-medium text-gray-700">Tamaño:</span>
                      <div class="flex items-center gap-1">
                        <button 
                          @click="magnifyingGlassRadius = Math.max(35, magnifyingGlassRadius - 5)"
                          class="px-2 py-1 bg-indigo-600 text-white text-xs font-bold rounded hover:bg-indigo-700 transition-all duration-300"
                          :disabled="magnifyingGlassRadius <= 35"
                          title="Reducir tamaño"
                        >
                          -
                        </button>
                        <span class="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded min-w-[45px] text-center">
                          {{ Math.round(adaptiveMagnifyingGlassRadius) }}
                        </span>
                        <button 
                          @click="magnifyingGlassRadius = Math.min(100, magnifyingGlassRadius + 5)"
                          class="px-2 py-1 bg-indigo-600 text-white text-xs font-bold rounded hover:bg-indigo-700 transition-all duration-300"
                          :disabled="magnifyingGlassRadius >= 100"
                          title="Aumentar tamaño"
                        >
                          +
                        </button>
                      </div>
                    </div>
                    
                    <!-- Help text -->
                    <div class="text-xs text-purple-600 text-center space-y-1 mt-2">
                      <p>🎯 Borde = color del objeto más cercano</p>
                      <p class="text-xs text-gray-500">
                        💡 Flecha con fondo = dentro del objeto
                      </p>
                      <p class="text-xs text-gray-500">
                        <kbd class="px-1 py-0.5 bg-gray-200 rounded text-xs">+/-</kbd> zoom, 
                        <kbd class="px-1 py-0.5 bg-gray-200 rounded text-xs">[/]</kbd> tamaño, 
                        <kbd class="px-1 py-0.5 bg-gray-200 rounded text-xs">ESC</kbd> salir
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Main image display area - much larger -->
          <div class="relative w-full" style="min-height: 400px;">
            <!-- Hidden image for canvas drawing -->
            <img 
              v-if="currentResultImage"
              :src="currentResultImage" 
              alt="Hidden image for canvas"
              ref="hiddenImage"
              @load="onImageLoad"
              @error="handleImageError"
              style="display: none;"
            />
            
            <!-- Show backend result image (with boxes) when not in box control mode -->
            <img 
              v-if="currentResultImage && !showBoxControls" 
              :src="currentResultImage" 
              alt="Resultado del análisis" 
              class="w-full max-h-[600px] mx-auto rounded-lg object-contain"
            />
            
            <!-- Show canvas (image + boxes) in box control mode -->
            <canvas 
              v-if="showBoxControls && currentResultImage"
              ref="imageCanvas"
              class="w-full max-h-[600px] mx-auto rounded-lg border border-green-300"
              :class="{ 
                'cursor-crosshair': !magnifyingGlassActive, 
                'cursor-none': magnifyingGlassActive 
              }"
              @click="handleCanvasClick"
              @dblclick="handleCanvasDoubleClick"
              @mousemove="handleCanvasMouseMove"
              @mouseleave="handleCanvasMouseLeave"
            ></canvas>
          </div>
        </div>

        <!-- Metadata and statistics -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          <!-- Analysis summary -->
          <div class="bg-white/80 p-3 sm:p-4 rounded-lg text-left">
            <h3 class="font-semibold text-gray-800 mb-3">Resumen del Análisis</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Estado:</span>
                <span class="font-medium text-green-700">Completado exitosamente</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Imagen procesada:</span>
                <span class="font-medium break-all text-right flex-1 ml-2">{{ selectedFile?.name }}</span>
              </div>
              <div v-if="avgConfidence !== null" class="flex justify-between">
                <span class="text-gray-600">Confianza promedio:</span>
                <span class="font-medium text-blue-700">{{ Math.round(avgConfidence * 100) }}%</span>
              </div>
              <div v-if="detectedBoxes.length > 0" class="flex justify-between">
                <span class="text-gray-600">Objetos detectados:</span>
                <span class="font-medium text-purple-700">{{ detectedBoxes.length }}</span>
              </div>
            </div>
          </div>

          <!-- Class distribution -->
          <div v-if="classCountSummary" class="bg-white/80 p-3 sm:p-4 rounded-lg">
            <h3 class="font-semibold text-gray-800 mb-3">Distribución por Clase</h3>
            <div class="space-y-2">
              <div 
                v-for="(count, className) in classCountSummary" 
                :key="className"
                class="flex items-center justify-between text-sm"
              >
                <div class="flex items-center gap-2">
                  <div 
                    class="w-3 h-3 rounded-sm border border-gray-400"
                    :style="{ backgroundColor: getColorForClass(className) }"
                  ></div>
                  <span class="text-gray-700">{{ className }}</span>
                </div>
                <span class="font-medium text-gray-900">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full max-w-md mx-auto">
          <button 
            @click="downloadResults"
            data-download-button
            class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-indigo-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-indigo-700 transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            💾 Descargar Resultados
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useAuth } from '../../composables/use_auth.js'
import { useInference } from '../../composables/send_inference.js'
import { useMinioMetadata } from '../../composables/use_minio_metadata.js'
import { useModels } from '../../composables/use_models.js'
import { useToast } from "vue-toastification"

// Authentication
const { isLoggedIn, user, loading: authLoading, checkAuthStatus } = useAuth()

// Toast notifications
const toast = useToast()

// File handling
const fileInput = ref(null)
const previewImage = ref(null)
const selectedFile = ref(null)

// Inference handling
const { loading, error, result, handleInference } = useInference()

// Minio metadata handling
const { 
  loading: metadataLoading, 
  error: metadataError, 
  detectedBoxes, 
  classCountSummary,
  fetchMetadata,
  getCachedConfidence,
  getBoxColor
} = useMinioMetadata()

// Model selection
const { 
  loading: modelsLoading, 
  error: modelsError, 
  models, 
  fetchModels 
} = useModels()
const selectedModel = ref(null)

// Box controls
const showBoxControls = ref(false)
const selectedBox = ref(null)
const controlPanelExpanded = ref(false)
const imageCanvas = ref(null)
const hiddenImage = ref(null)
const canvasContext = ref(null)
const canvasImageBounds = ref(null)

// Magnifying glass controls
const magnifyingGlassActive = ref(false)
const magnifyingGlassRadius = ref(50) // Smaller default radius
const magnifyingGlassPosition = ref({ x: 0, y: 0 })
const magnifyingGlassZoom = ref(1.0) // Zoom factor
const magnifyingGlassBoxes = ref([]) // Boxes closest to magnifying glass crosshair

// Computed properties
const currentResultImage = computed(() => {
  if (!result.value) return null
  
  // If controls are hidden, show the normal results image with boxes already drawn
  if (!showBoxControls.value) {
    return result.value.generatedImgUrl
  }
  // If controls are visible, show the original image (without boxes)
  return result.value.baseImageUrl || result.value.generatedImgUrl
})

const avgConfidence = computed(() => {
  if (!result.value?.id) return null
  return getCachedConfidence(result.value.id)
})

// Computed magnifying glass radius based on image size and zoom
const adaptiveMagnifyingGlassRadius = computed(() => {
  if (!canvasImageBounds.value || !imageCanvas.value) {
    return magnifyingGlassRadius.value
  }
  
  const bounds = canvasImageBounds.value
  const canvas = imageCanvas.value
  
  // Calculate a base radius that's proportional to the smaller dimension of the displayed image
  const imageDisplayWidth = bounds.drawWidth
  const imageDisplayHeight = bounds.drawHeight
  const smallerDimension = Math.min(imageDisplayWidth, imageDisplayHeight)
  
  // Base radius is 8-15% of the smaller dimension, adjusted by user setting
  const baseRadius = (smallerDimension * 0.12) * (magnifyingGlassRadius.value / 50)
  
  // Inverse relationship with zoom - higher zoom = smaller radius for precision
  // More gentle scaling for better UX at high zooms
  const zoomAdjustedRadius = baseRadius * (1.8 / (magnifyingGlassZoom.value + 0.5))
  
  // Ensure minimum and maximum bounds with better scaling
  return Math.max(30, Math.min(zoomAdjustedRadius, 150))
})

// Watch for result changes to fetch metadata
watch(result, async (newResult) => {
  if (newResult && newResult.id) {
    await fetchMetadata(newResult.id)
  }
}, { immediate: true })

// Check auth status on mount
onMounted(async () => {
  checkAuthStatus()
  // Fetch models when component mounts if user is logged in
  if (isLoggedIn.value) {
    await fetchModels()
    // Set default model selection to first available model
    if (models.value.length > 0) {
      selectedModel.value = models.value[0].id
    }
  }
  
  // Add keyboard event listeners for magnifying glass controls
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  // Clean up keyboard event listeners
  window.removeEventListener('keydown', handleKeyDown)
})

// Keyboard shortcuts for magnifying glass controls
const handleKeyDown = (event) => {
  // Only handle keys when magnifying glass is active and showing box controls
  if (!magnifyingGlassActive.value || !showBoxControls.value) return
  
  // Prevent default behavior for handled keys
  const handledKeys = ['Equal', 'Minus', 'BracketLeft', 'BracketRight', 'Escape']
  if (handledKeys.includes(event.code)) {
    event.preventDefault()
  }
  
  switch (event.code) {
    case 'Equal': // Plus key (for zoom in)
    case 'NumpadAdd':
      magnifyingGlassZoom.value = Math.min(6.0, magnifyingGlassZoom.value + 0.2)
      break
    case 'Minus': // Minus key (for zoom out)
    case 'NumpadSubtract':
      magnifyingGlassZoom.value = Math.max(1.0, magnifyingGlassZoom.value - 0.2)
      break
    case 'BracketLeft': // [ key (decrease size)
      magnifyingGlassRadius.value = Math.max(35, magnifyingGlassRadius.value - 5)
      break
    case 'BracketRight': // ] key (increase size)
      magnifyingGlassRadius.value = Math.min(100, magnifyingGlassRadius.value + 5)
      break
    case 'Escape': // ESC key (exit magnifying glass)
      toggleMagnifyingGlass()
      break
  }
}

// Watch for login status changes to fetch models
watch(isLoggedIn, async (newValue) => {
  if (newValue) {
    await fetchModels()
    if (models.value.length > 0) {
      selectedModel.value = models.value[0].id
    }
  }
})

function triggerFileInput() {
  if (loading.value) return
  fileInput.value.click()
}

function onFileChange(event) {
  const file = event.target.files[0]
  if (file && file.type.startsWith("image/")) {
    previewImage.value = URL.createObjectURL(file)
    selectedFile.value = file
  } else if (file) {
    toast.error('Por favor selecciona un archivo de imagen válido (JPG, PNG, WebP)')
  }
}

function resetImage() {
  previewImage.value = null
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ""
  }
}

async function startInference() {
  if (!selectedFile.value) {
    toast.error('Por favor selecciona una imagen primero')
    return
  }
  
  if (!isLoggedIn.value) {
    toast.error('Debes iniciar sesión para usar esta funcionalidad')
    return
  }

  if (!selectedModel.value) {
    toast.error('Por favor selecciona un modelo primero')
    return
  }

  await handleInference(selectedFile.value, selectedModel.value)
}

function startNewAnalysis() {
  resetImage()
  result.value = null
  error.value = ''  // Clear previous errors
  showBoxControls.value = false
  selectedBox.value = null
}

const toggleMagnifyingGlass = () => {
  magnifyingGlassActive.value = !magnifyingGlassActive.value
  if (magnifyingGlassActive.value) {
    // Set initial position to center of canvas
    if (imageCanvas.value) {
      const rect = imageCanvas.value.getBoundingClientRect()
      magnifyingGlassPosition.value = {
        x: rect.width / 2,
        y: rect.height / 2
      }
    }
  }
  updateImageWithBoxes()
}

const updateMagnifyingGlassPosition = (event) => {
  if (!magnifyingGlassActive.value || !imageCanvas.value) return
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = (event.clientX - rect.left) * (canvas.width / rect.width)
  const y = (event.clientY - rect.top) * (canvas.height / rect.height)
  
  magnifyingGlassPosition.value = { x, y }
  
  // Find boxes within magnifying glass area
  findBoxesInMagnifyingGlass(x, y)
  
  updateImageWithBoxes()
}

const findBoxesInMagnifyingGlass = (centerX, centerY) => {
  const bounds = canvasImageBounds.value
  
  if (!bounds) {
    magnifyingGlassBoxes.value = []
    return
  }
  

  const boxDistances = detectedBoxes.value
    .filter(box => box.visible && box.bbox_normalized)
    .map(box => {
      const { x1, y1, x2, y2 } = box.bbox_normalized
      
      // Convert normalized coordinates to canvas coordinates
      const canvasX1 = x1 * bounds.drawWidth + bounds.drawX
      const canvasY1 = y1 * bounds.drawHeight + bounds.drawY
      const canvasX2 = x2 * bounds.drawWidth + bounds.drawX
      const canvasY2 = y2 * bounds.drawHeight + bounds.drawY
      
      // Calculate box center and bounds
      const boxCenterX = (canvasX1 + canvasX2) / 2
      const boxCenterY = (canvasY1 + canvasY2) / 2
      const boxLeft = Math.min(canvasX1, canvasX2)
      const boxRight = Math.max(canvasX1, canvasX2)
      const boxTop = Math.min(canvasY1, canvasY2)
      const boxBottom = Math.max(canvasY1, canvasY2)
      
      // Calculate distance from crosshair to box center
      const distanceToCenter = Math.sqrt(
        Math.pow(centerX - boxCenterX, 2) + Math.pow(centerY - boxCenterY, 2)
      )
      
      // Check if crosshair is inside the box
      const isInside = centerX >= boxLeft && centerX <= boxRight && 
                      centerY >= boxTop && centerY <= boxBottom
      
      // Calculate distance from crosshair to nearest box edge if outside
      let distanceToBox = distanceToCenter
      if (!isInside) {
        const distanceToLeft = Math.abs(centerX - boxLeft)
        const distanceToRight = Math.abs(centerX - boxRight)
        const distanceToTop = Math.abs(centerY - boxTop)
        const distanceToBottom = Math.abs(centerY - boxBottom)
        
        if (centerX < boxLeft) {
          if (centerY < boxTop) {
            // Top-left corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxLeft, 2) + Math.pow(centerY - boxTop, 2))
          } else if (centerY > boxBottom) {
            // Bottom-left corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxLeft, 2) + Math.pow(centerY - boxBottom, 2))
          } else {
            // Left edge
            distanceToBox = distanceToLeft
          }
        } else if (centerX > boxRight) {
          if (centerY < boxTop) {
            // Top-right corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxRight, 2) + Math.pow(centerY - boxTop, 2))
          } else if (centerY > boxBottom) {
            // Bottom-right corner
            distanceToBox = Math.sqrt(Math.pow(centerX - boxRight, 2) + Math.pow(centerY - boxBottom, 2))
          } else {
            // Right edge
            distanceToBox = distanceToRight
          }
        } else {
          // Above or below
          distanceToBox = centerY < boxTop ? distanceToTop : distanceToBottom
        }
      } else {
        // Inside the box - use negative distance for priority
        distanceToBox = -Math.min(
          Math.min(centerX - boxLeft, boxRight - centerX),
          Math.min(centerY - boxTop, boxBottom - centerY)
        )
      }
      
      return {
        ...box,
        distanceToCenter,
        distanceToBox,
        isInside
      }
    })
    .sort((a, b) => {
      // Prioritize boxes containing the crosshair, then by distance
      if (a.isInside && !b.isInside) return -1
      if (!a.isInside && b.isInside) return 1
      
      // For boxes both inside or both outside, sort by distance
      return a.distanceToBox - b.distanceToBox
    })
  
  // Take the closest boxes (up to 5) within a reasonable range
  const maxDistance = 150 // Maximum distance to consider a box "relevant"
  magnifyingGlassBoxes.value = boxDistances
    .filter(box => box.isInside || box.distanceToBox <= maxDistance)
    .slice(0, 5) // Limit to 5 boxes for performance
    .map(box => {
      // Set intersection area for compatibility with existing code
      // Higher values for closer boxes or boxes containing the crosshair
      if (box.isInside) {
        box.intersectionArea = 1.0 - (box.distanceToCenter / 1000) // High priority for inside boxes
      } else {
        box.intersectionArea = Math.max(0, 1.0 - (box.distanceToBox / maxDistance))
      }
      return box
    })
}

const toggleBoxControls = async () => {
  showBoxControls.value = !showBoxControls.value
  
  if (showBoxControls.value) {
    // Wait for next tick to ensure DOM is updated
    await nextTick()
    
    // Ensure we have a valid image and canvas
    if (imageCanvas.value && hiddenImage.value && hiddenImage.value.complete && detectedBoxes.value.length > 0) {
      setupCanvas()
      drawImageWithBoxes()
    }
  } else {
    // Clear selection and context when exiting edit mode
    selectedBox.value = null
    if (canvasContext.value && imageCanvas.value) {
      canvasContext.value.clearRect(0, 0, imageCanvas.value.width, imageCanvas.value.height)
    }
  }
}

const toggleAllBoxes = (visible) => {
  detectedBoxes.value.forEach(box => {
    box.visible = visible
  })
  updateImageWithBoxes()
}

const selectBox = (box) => {
  const previousSelection = selectedBox.value
  selectedBox.value = previousSelection === box ? null : box
  
  // Redraw canvas to show selection highlighting if in box control mode
  if (showBoxControls.value && canvasContext.value) {
    updateImageWithBoxes()
  }
}

const updateImageWithBoxes = () => {
  if (showBoxControls.value && canvasContext.value) {
    drawImageWithBoxes()
  }
}

const onImageLoad = () => {
  // Always set up canvas when image loads, regardless of current mode
  if (hiddenImage.value && hiddenImage.value.complete && hiddenImage.value.naturalHeight !== 0) {
    nextTick(() => {
      if (showBoxControls.value && imageCanvas.value) {
        setupCanvas()
        if (detectedBoxes.value.length > 0) {
          drawImageWithBoxes()
        }
      }
    })
  }
}

const setupCanvas = () => {
  if (!imageCanvas.value || !hiddenImage.value) {
    return
  }
  
  const canvas = imageCanvas.value
  const img = hiddenImage.value
  const ctx = canvas.getContext('2d')
  canvasContext.value = ctx

  // Get the actual display size from the parent container
  const containerRect = canvas.parentElement.getBoundingClientRect()
  const containerWidth = containerRect.width
  
  // Calculate the actual display size based on max-h-[600px] and object-contain
  const maxHeight = 600
  const imageAspectRatio = img.naturalWidth / img.naturalHeight
  
  let displayWidth, displayHeight
  
  // Calculate actual display dimensions using object-contain logic
  if (containerWidth / maxHeight > imageAspectRatio) {
    // Height is the limiting factor
    displayHeight = Math.min(maxHeight, img.naturalHeight)
    displayWidth = displayHeight * imageAspectRatio
  } else {
    // Width is the limiting factor
    displayWidth = containerWidth
    displayHeight = displayWidth / imageAspectRatio
    if (displayHeight > maxHeight) {
      displayHeight = maxHeight
      displayWidth = displayHeight * imageAspectRatio
    }
  }
  
  // Set canvas size to match the actual displayed image size
  canvas.width = displayWidth
  canvas.height = displayHeight
  canvas.style.width = `${displayWidth}px`
  canvas.style.height = `${displayHeight}px`

  // Configure canvas context for better rendering
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'

  // Calculate object-contain bounds for the image (now canvas fills exactly the image area)
  const canvasAspectRatio = displayWidth / displayHeight
  
  let drawWidth, drawHeight, drawX, drawY
  
  // Since canvas size matches display size, draw the image to fill the entire canvas
  drawWidth = displayWidth
  drawHeight = displayHeight
  drawX = 0
  drawY = 0
  
  // Store bounds for use in drawing and hit-testing
  canvasImageBounds.value = {
    drawX,
    drawY,
    drawWidth,
    drawHeight,
    scaleX: drawWidth / img.naturalWidth,
    scaleY: drawHeight / img.naturalHeight
  }
}

const drawImageWithBoxes = () => {
  if (!canvasContext.value || !hiddenImage.value || !canvasImageBounds.value) {
    return
  }
  
  const ctx = canvasContext.value
  const canvas = imageCanvas.value
  const img = hiddenImage.value
  const bounds = canvasImageBounds.value

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Draw the image first
  ctx.drawImage(img, bounds.drawX, bounds.drawY, bounds.drawWidth, bounds.drawHeight)

  // Only draw bounding boxes if magnifying glass is not active
  if (!magnifyingGlassActive.value) {
    // Get visible boxes with normalized coordinates
    const visibleBoxes = detectedBoxes.value.filter(box => box.visible && box.bbox_normalized)
    
    if (visibleBoxes.length > 0) {
      // Draw non-selected boxes first, then selected box on top
      const nonSelectedBoxes = visibleBoxes.filter(box => box !== selectedBox.value)
      const selectedBoxToDrawLast = visibleBoxes.find(box => box === selectedBox.value)
      
      // Reset line dash before drawing
      ctx.setLineDash([])
      
      // Draw non-selected boxes
      nonSelectedBoxes.forEach((box) => {
        drawBoundingBox(ctx, box)
      })
      
      // Draw selected box on top
      if (selectedBoxToDrawLast) {
        drawBoundingBox(ctx, selectedBoxToDrawLast)
      }
    }
  } else {
    // Draw magnifying glass
    drawMagnifyingGlass(ctx)
  }
}

const drawBoundingBox = (ctx, box) => {
  const { bbox_normalized, color, label, confidence } = box
  const bounds = canvasImageBounds.value
  
  if (!bounds || !bbox_normalized) return
  
  // Use normalized coordinates (0-1) and map directly to canvas drawing area
  const { x1, y1, x2, y2 } = bbox_normalized
  
  // Convert normalized coordinates to canvas coordinates within the image bounds
  const canvasX1 = x1 * bounds.drawWidth + bounds.drawX
  const canvasY1 = y1 * bounds.drawHeight + bounds.drawY
  const canvasX2 = x2 * bounds.drawWidth + bounds.drawX
  const canvasY2 = y2 * bounds.drawHeight + bounds.drawY
  
  const x = Math.min(canvasX1, canvasX2)
  const y = Math.min(canvasY1, canvasY2)
  const width = Math.abs(canvasX2 - canvasX1)
  const height = Math.abs(canvasY2 - canvasY1)
  
  if (width <= 0 || height <= 0) return
  
  const isSelected = selectedBox.value === box
  
  // Draw bounding box
  ctx.strokeStyle = color
  ctx.lineWidth = isSelected ? 4 : 2
  ctx.setLineDash(isSelected ? [5, 5] : [])
  ctx.strokeRect(x, y, width, height)
  
  // Fill selected box with semi-transparent color
  if (isSelected) {
    ctx.fillStyle = color + '20'
    ctx.fillRect(x, y, width, height)
  }
  
  // Draw label
  const labelText = `${label} ${Math.round(confidence * 100)}%`
  ctx.font = isSelected ? 'bold 12px Inter, system-ui, sans-serif' : '12px Inter, system-ui, sans-serif'
  const textMetrics = ctx.measureText(labelText)
  const labelWidth = textMetrics.width + 8
  const labelHeight = 20
  const labelY = y > labelHeight ? y - labelHeight : y + height + labelHeight
  
  ctx.fillStyle = isSelected ? '#7C3AED' : color
  ctx.fillRect(x, labelY, labelWidth, labelHeight)
  ctx.fillStyle = 'white'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillText(labelText, x + 4, labelY + labelHeight / 2)
}

const handleCanvasClick = (event) => {
  if (!showBoxControls.value || !canvasContext.value || !imageCanvas.value) return
  
  if (magnifyingGlassActive.value) return // Don't handle clicks when magnifying glass is active
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = (event.clientX - rect.left) * (canvas.width / rect.width)
  const y = (event.clientY - rect.top) * (canvas.height / rect.height)
  
  const clickedBox = findBoxAtPosition(x, y)
  selectBox(clickedBox)
}

const handleCanvasDoubleClick = (event) => {
  if (!showBoxControls.value || !canvasContext.value || !imageCanvas.value) return
  
  if (magnifyingGlassActive.value) return // Don't handle double clicks when magnifying glass is active
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = (event.clientX - rect.left) * (canvas.width / rect.width)
  const y = (event.clientY - rect.top) * (canvas.height / rect.height)
  
  const clickedBox = findBoxAtPosition(x, y)
  if (clickedBox) {
    clickedBox.visible = !clickedBox.visible
    updateImageWithBoxes()
  }
}

const handleCanvasMouseMove = (event) => {
  if (magnifyingGlassActive.value) {
    updateMagnifyingGlassPosition(event)
  }
}

const handleCanvasMouseLeave = () => {
  if (magnifyingGlassActive.value) {
    magnifyingGlassBoxes.value = []
    updateImageWithBoxes()
  }
}

const findBoxAtPosition = (x, y) => {
  const bounds = canvasImageBounds.value
  
  if (!bounds) {
    return null
  }
  
  // Check boxes from last drawn (on top) to first drawn (on bottom)
  for (let i = detectedBoxes.value.length - 1; i >= 0; i--) {
    const box = detectedBoxes.value[i]
    if (!box.visible || !box.bbox_normalized) continue
    
    const { x1, y1, x2, y2 } = box.bbox_normalized
    
    // Convert normalized coordinates to canvas coordinates (same as drawing logic)
    const canvasX1 = x1 * bounds.drawWidth + bounds.drawX
    const canvasY1 = y1 * bounds.drawHeight + bounds.drawY
    const canvasX2 = x2 * bounds.drawWidth + bounds.drawX
    const canvasY2 = y2 * bounds.drawHeight + bounds.drawY
    
    const boxX = Math.min(canvasX1, canvasX2)
    const boxY = Math.min(canvasY1, canvasY2)
    const boxWidth = Math.abs(canvasX2 - canvasX1)
    const boxHeight = Math.abs(canvasY2 - canvasY1)
    
    if (x >= boxX && x <= boxX + boxWidth && y >= boxY && y <= boxY + boxHeight) {
      return box
    }
  }
  return null
}

const drawMagnifyingGlass = (ctx) => {
  if (!magnifyingGlassActive.value || !hiddenImage.value || !canvasImageBounds.value) return
  
  const { x, y } = magnifyingGlassPosition.value
  const radius = adaptiveMagnifyingGlassRadius.value
  const zoom = magnifyingGlassZoom.value
  const bounds = canvasImageBounds.value
  const img = hiddenImage.value
  
  // Save current context state
  ctx.save()
  
  // Create circular clipping path
  ctx.beginPath()
  ctx.arc(x, y, radius, 0, 2 * Math.PI)
  ctx.clip()
  
  // Clear the clipped area
  ctx.clearRect(x - radius, y - radius, radius * 2, radius * 2)
  
  // Calculate source coordinates on the original image
  const sourceX = ((x - bounds.drawX) / bounds.drawWidth) * img.naturalWidth
  const sourceY = ((y - bounds.drawY) / bounds.drawHeight) * img.naturalHeight
  const sourceSize = (radius * 2) / zoom
  
  // Draw zoomed image portion
  ctx.drawImage(
    img,
    sourceX - sourceSize / 2, sourceY - sourceSize / 2, sourceSize, sourceSize,
    x - radius, y - radius, radius * 2, radius * 2
  )
  
  // Restore context to remove clipping
  ctx.restore()
  
  // Draw magnifying glass border with color coding
  drawMagnifyingGlassBorder(ctx, x, y, radius)
  
  // Draw directional guidance
  drawMagnifyingGlassGuidance(ctx, x, y, radius)
  
  // Draw box information overlay
  drawMagnifyingGlassOverlay(ctx, x, y, radius)
}

const drawMagnifyingGlassBorder = (ctx, centerX, centerY, radius) => {
  const borderWidth = 4
  
  ctx.lineWidth = borderWidth
  
  if (magnifyingGlassBoxes.value.length === 0) {
    // Default gray border when no boxes
    ctx.strokeStyle = '#6B7280'
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
    ctx.stroke()
  } else {
    // Use the color of the most dominant box (largest intersection area)
    const dominantBox = magnifyingGlassBoxes.value[0] // Already sorted by area, largest first
    
    // Draw main border in dominant box color
    ctx.strokeStyle = dominantBox.color
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
    ctx.stroke()
    
    // Draw corner indicators for other boxes (if any)
    if (magnifyingGlassBoxes.value.length > 1) {
      const indicatorSize = 8
      
      // Calculate safe distance outside the magnifying glass based on radius and zoom
      // Ensure indicators are always outside the visible content area
      const minSafeDistance = 16 // Minimum distance from circle edge
      const dynamicOffset = Math.max(minSafeDistance, radius * 0.25) // Scale with magnifying glass size
      const safeDistance = radius + dynamicOffset
      
      // Position indicators outside the magnifying glass circle
      const corners = [
        { x: centerX + Math.cos(-Math.PI/4) * safeDistance, y: centerY + Math.sin(-Math.PI/4) * safeDistance }, // Top-right (diagonal)
        { x: centerX + Math.cos(Math.PI/4) * safeDistance, y: centerY + Math.sin(Math.PI/4) * safeDistance },   // Bottom-right (diagonal)
        { x: centerX + Math.cos(3*Math.PI/4) * safeDistance, y: centerY + Math.sin(3*Math.PI/4) * safeDistance }, // Bottom-left (diagonal)
        { x: centerX + Math.cos(-3*Math.PI/4) * safeDistance, y: centerY + Math.sin(-3*Math.PI/4) * safeDistance }  // Top-left (diagonal)
      ]
      
      // Show up to 4 additional boxes in corners
      magnifyingGlassBoxes.value.slice(1, 5).forEach((box, index) => {
        const corner = corners[index]
        if (corner) {
          // Check if indicator would be within canvas bounds
          const canvas = imageCanvas.value
          if (corner.x - indicatorSize/2 >= 0 && corner.x + indicatorSize/2 <= canvas.width &&
              corner.y - indicatorSize/2 >= 0 && corner.y + indicatorSize/2 <= canvas.height) {
            
            // Draw small colored square indicator with shadow for better visibility
            ctx.shadowColor = 'rgba(0, 0, 0, 0.3)'
            ctx.shadowBlur = 3
            ctx.shadowOffsetX = 1
            ctx.shadowOffsetY = 1
            
            ctx.fillStyle = box.color
            ctx.fillRect(
              corner.x - indicatorSize / 2, 
              corner.y - indicatorSize / 2, 
              indicatorSize, 
              indicatorSize
            )
            
            // Reset shadow
            ctx.shadowColor = 'transparent'
            ctx.shadowBlur = 0
            ctx.shadowOffsetX = 0
            ctx.shadowOffsetY = 0
            
            // Add white border to indicator for better visibility
            ctx.strokeStyle = 'white'
            ctx.lineWidth = 2
            ctx.strokeRect(
              corner.x - indicatorSize / 2, 
              corner.y - indicatorSize / 2, 
              indicatorSize, 
              indicatorSize
            )
          }
        }
      })
    }
  }
  
  // Add outer highlight
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.arc(centerX, centerY, radius + borderWidth / 2 + 1, 0, 2 * Math.PI)
  ctx.stroke()
  
  // Add inner border for depth effect
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.arc(centerX, centerY, radius - 1, 0, 2 * Math.PI)
  ctx.stroke()
}

const drawMagnifyingGlassGuidance = (ctx, centerX, centerY, radius) => {
  const crosshairSize = Math.min(12, radius * 0.2)
  
  // Check if we have a dominant box to guide towards
  const dominantBox = magnifyingGlassBoxes.value.length > 0 ? magnifyingGlassBoxes.value[0] : null
  
  if (dominantBox && dominantBox.bbox_normalized && canvasImageBounds.value) {
    const bounds = canvasImageBounds.value
    const { x1, y1, x2, y2 } = dominantBox.bbox_normalized
    
    // Calculate box center in canvas coordinates
    const boxCenterX = ((x1 + x2) / 2) * bounds.drawWidth + bounds.drawX
    const boxCenterY = ((y1 + y2) / 2) * bounds.drawHeight + bounds.drawY
    
    // Use the distance data we already calculated
    const distanceToBoxCenter = dominantBox.distanceToCenter || 0
    const isInsideBox = dominantBox.isInside || false
    
    // Be more strict about when to show special states
    // Only show "near center" when actually close to center (within 8px)
    const isNearBoxCenter = distanceToBoxCenter < 8
    // Only show "inside box" indicators when BOTH inside the box AND close to center
    const showInsideBoxState = isInsideBox && isNearBoxCenter
    
    // Always show arrow - it provides useful distance information
    const shouldShowArrow = true
    
    if (shouldShowArrow) {
      // Calculate direction to box center
      const deltaX = boxCenterX - centerX
      const deltaY = boxCenterY - centerY
      
      // Draw directional arrow pointing to box center
      const angle = Math.atan2(deltaY, deltaX)
      const arrowDistance = radius * 0.6 // Position arrow inside the magnifying glass
      const arrowX = centerX + Math.cos(angle) * arrowDistance
      const arrowY = centerY + Math.sin(angle) * arrowDistance
      
      // Use different arrow style when inside the box vs outside
      // Use box color with better contrast instead of gold
      let arrowBgColor
      if (isInsideBox) {
        arrowBgColor = dominantBox.color
      } else {
        arrowBgColor = 'rgba(0, 0, 0, 0.8)'
      }
      
      // Draw arrow background (semi-transparent circle) - make it bigger when inside box
      const bgRadius = isInsideBox ? 10 : 8
      ctx.fillStyle = arrowBgColor
      ctx.beginPath()
      ctx.arc(arrowX, arrowY, bgRadius, 0, 2 * Math.PI)
      ctx.fill()
      
      // Draw arrow pointing to box center
      const arrowSize = isInsideBox ? 7 : 6 // Slightly bigger when inside
      ctx.fillStyle = isInsideBox ? 'white' : dominantBox.color // Inverted colors for better contrast
      ctx.strokeStyle = isInsideBox ? 'rgba(0, 0, 0, 0.5)' : 'white' 
      ctx.lineWidth = 2
      
      ctx.beginPath()
      ctx.moveTo(
        arrowX + Math.cos(angle) * arrowSize,
        arrowY + Math.sin(angle) * arrowSize
      )
      ctx.lineTo(
        arrowX + Math.cos(angle + 2.5) * arrowSize * 0.6,
        arrowY + Math.sin(angle + 2.5) * arrowSize * 0.6
      )
      ctx.lineTo(
        arrowX + Math.cos(angle - 2.5) * arrowSize * 0.6,
        arrowY + Math.sin(angle - 2.5) * arrowSize * 0.6
      )
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
      
      // Draw distance indicator text with consistent styling
      const distance = Math.round(distanceToBoxCenter)
      ctx.font = 'bold 10px Inter'
      ctx.fillStyle = 'white'
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)'
      ctx.lineWidth = 2
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // Position text near the arrow
      const textX = arrowX + Math.cos(angle + Math.PI/2) * 15
      const textY = arrowY + Math.sin(angle + Math.PI/2) * 15
      
      // Add subtle prefix when inside box to clarify
      const displayText = isInsideBox ? `→ ${distance}px` : `${distance}px`
      
      ctx.strokeText(displayText, textX, textY)
      ctx.fillText(displayText, textX, textY)
    }
    
    // Draw enhanced crosshair based on strict conditions
    if (showInsideBoxState) {
      // Special "inside box and near center" crosshair - this is the target state
      drawBullseyeCrosshair(ctx, centerX, centerY, crosshairSize, dominantBox.color, true)
    } else if (isNearBoxCenter) {
      // Just near center but not inside box - regular bullseye
      drawBullseyeCrosshair(ctx, centerX, centerY, crosshairSize, dominantBox.color, false)
    } else {
      // Standard crosshair with direction hint
      const deltaX = boxCenterX - centerX
      const deltaY = boxCenterY - centerY
      drawStandardCrosshair(ctx, centerX, centerY, crosshairSize, dominantBox.color, deltaX, deltaY)
    }
  } else {
    // No dominant box - draw standard neutral crosshair
    drawStandardCrosshair(ctx, centerX, centerY, crosshairSize, '#6B7280', 0, 0)
  }
}

const drawBullseyeCrosshair = (ctx, centerX, centerY, size, boxColor, isInsideBox = false) => {
  if (isInsideBox) {
    // DRAMATICALLY DIFFERENT: Solid filled circle with crosshair overlay - "TARGET ACQUIRED"
    
    // Large filled circle background
    ctx.fillStyle = `${boxColor}E0` // Semi-transparent
    ctx.beginPath()
    ctx.arc(centerX, centerY, size * 0.8, 0, 2 * Math.PI)
    ctx.fill()
    
    // Solid border
    ctx.strokeStyle = boxColor
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.arc(centerX, centerY, size * 0.8, 0, 2 * Math.PI)
    ctx.stroke()
    
    // White crosshair overlay (thick and bold)
    const crossSize = size * 0.6
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 4
    ctx.setLineDash([])
    
    // Horizontal line
    ctx.beginPath()
    ctx.moveTo(centerX - crossSize, centerY)
    ctx.lineTo(centerX + crossSize, centerY)
    ctx.stroke()
    
    // Vertical line
    ctx.beginPath()
    ctx.moveTo(centerX, centerY - crossSize)
    ctx.lineTo(centerX, centerY + crossSize)
    ctx.stroke()
    
    // Add black outline to crosshair
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)'
    ctx.lineWidth = 6
    
    // Horizontal line outline
    ctx.beginPath()
    ctx.moveTo(centerX - crossSize, centerY)
    ctx.lineTo(centerX + crossSize, centerY)
    ctx.stroke()
    
    // Vertical line outline
    ctx.beginPath()
    ctx.moveTo(centerX, centerY - crossSize)
    ctx.lineTo(centerX, centerY + crossSize)
    ctx.stroke()
    
    // Redraw white crosshair on top
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 4
    
    // Horizontal line
    ctx.beginPath()
    ctx.moveTo(centerX - crossSize, centerY)
    ctx.lineTo(centerX + crossSize, centerY)
    ctx.stroke()
    
    // Vertical line
    ctx.beginPath()
    ctx.moveTo(centerX, centerY - crossSize)
    ctx.lineTo(centerX, centerY + crossSize)
    ctx.stroke()
    
    // Success indicator text
    ctx.font = 'bold 8px Inter'
    ctx.fillStyle = 'white'
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.7)'
    ctx.lineWidth = 2
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.strokeText('TARGET', centerX, centerY + size + 8)
    ctx.fillText('TARGET', centerX, centerY + size + 8)
    
  } else {
    // COMPLETELY DIFFERENT: Traditional concentric rings - "APPROACHING TARGET"
    
    // Multiple thin rings (classic bullseye)
    const rings = [
      { radius: size * 0.8, color: boxColor, width: 2 },
      { radius: size * 0.6, color: 'rgba(255, 255, 255, 0.9)', width: 2 },
      { radius: size * 0.4, color: boxColor, width: 2 },
      { radius: size * 0.2, color: 'rgba(255, 255, 255, 0.9)', width: 2 }
    ]
    
    rings.forEach(ring => {
      ctx.strokeStyle = ring.color
      ctx.lineWidth = ring.width
      ctx.setLineDash([])
      ctx.beginPath()
      ctx.arc(centerX, centerY, ring.radius, 0, 2 * Math.PI)
      ctx.stroke()
    })
    
    // Small center dot
    ctx.fillStyle = boxColor
    ctx.beginPath()
    ctx.arc(centerX, centerY, 2, 0, 2 * Math.PI)
    ctx.fill()
    
    // Approaching indicator text
    ctx.font = 'bold 7px Inter'
    ctx.fillStyle = boxColor
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 2
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.strokeText('CLOSE', centerX, centerY + size + 8)
    ctx.fillText('CLOSE', centerX, centerY + size + 8)
  }
}

const drawStandardCrosshair = (ctx, centerX, centerY, size, color, deltaX, deltaY) => {
  // Standard crosshair with optional directional bias
  const hasDirection = deltaX !== 0 || deltaY !== 0
  
  // Make crosshair slightly biased toward the target direction
  const biasStrength = hasDirection ? Math.min(size * 0.3, 4) : 0
  const angle = hasDirection ? Math.atan2(deltaY, deltaX) : 0
  
  const offsetX = Math.cos(angle) * biasStrength
  const offsetY = Math.sin(angle) * biasStrength
  
  ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)'
  ctx.lineWidth = 2.5
  ctx.setLineDash([])
  
  // Vertical line with bias
  ctx.beginPath()
  ctx.moveTo(centerX + offsetX, centerY - size + offsetY)
  ctx.lineTo(centerX + offsetX, centerY + size + offsetY)
  ctx.stroke()
  
  // Horizontal line with bias
  ctx.beginPath()
  ctx.moveTo(centerX - size + offsetX, centerY + offsetY)
  ctx.lineTo(centerX + size + offsetX, centerY + offsetY)
  ctx.stroke()
  
  // White crosshair on top
  ctx.strokeStyle = hasDirection ? color : 'rgba(255, 255, 255, 0.8)'
  ctx.lineWidth = 1.5
  ctx.setLineDash([3, 2])
  
  // Vertical line
  ctx.beginPath()
  ctx.moveTo(centerX + offsetX, centerY - size + offsetY)
  ctx.lineTo(centerX + offsetX, centerY + size + offsetY)
  ctx.stroke()
  
  // Horizontal line
  ctx.beginPath()
  ctx.moveTo(centerX - size + offsetX, centerY + offsetY)
  ctx.lineTo(centerX + size + offsetX, centerY + offsetY)
  ctx.stroke()
  
  // Reset line dash
  ctx.setLineDash([])
}

const drawMagnifyingGlassOverlay = (ctx, centerX, centerY, radius) => {
  if (magnifyingGlassBoxes.value.length === 0) return
  
  // Position overlay to the side that has more space
  const canvas = imageCanvas.value
  const overlayWidth = 220
  const overlayHeight = Math.min(magnifyingGlassBoxes.value.length * 30 + 30, 200) // Cap height
  
  let overlayX, overlayY
  
  // Determine best position for overlay
  if (centerX + radius + overlayWidth + 10 < canvas.width) {
    // Right side
    overlayX = centerX + radius + 10
    overlayY = centerY - overlayHeight / 2
  } else if (centerX - radius - overlayWidth - 10 > 0) {
    // Left side
    overlayX = centerX - radius - overlayWidth - 10
    overlayY = centerY - overlayHeight / 2
  } else if (centerY - radius - overlayHeight - 10 > 0) {
    // Top
    overlayX = centerX - overlayWidth / 2
    overlayY = centerY - radius - overlayHeight - 10
  } else {
    // Bottom
    overlayX = centerX - overlayWidth / 2
    overlayY = centerY + radius + 10
  }
  
  // Ensure overlay stays within canvas bounds
  overlayX = Math.max(5, Math.min(overlayX, canvas.width - overlayWidth - 5))
  overlayY = Math.max(5, Math.min(overlayY, canvas.height - overlayHeight - 5))
  
  // Draw overlay background
  ctx.fillStyle = 'rgba(0, 0, 0, 0.85)'
  ctx.fillRect(overlayX, overlayY, overlayWidth, overlayHeight)
  
  // Draw overlay border
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
  ctx.lineWidth = 1
  ctx.strokeRect(overlayX, overlayY, overlayWidth, overlayHeight)
  
  // Draw header
  ctx.font = 'bold 12px Inter, system-ui, sans-serif'
  ctx.textAlign = 'left'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = 'white'
  ctx.fillText('Objetos detectados:', overlayX + 10, overlayY + 15)
  
  // Draw box information
  ctx.font = '11px Inter, system-ui, sans-serif'
  
  magnifyingGlassBoxes.value.slice(0, 6).forEach((box, index) => { // Show max 6 boxes
    const yPos = overlayY + 35 + index * 25
    const isDominant = index === 0
    
    // Highlight dominant box
    if (isDominant) {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'
      ctx.fillRect(overlayX + 5, yPos - 10, overlayWidth - 10, 20)
    }
    
    // Color indicator (larger for dominant box)
    const indicatorSize = isDominant ? 14 : 10
    ctx.fillStyle = box.color
    ctx.fillRect(overlayX + 10, yPos - indicatorSize/2, indicatorSize, indicatorSize)
    
    // White border for indicator
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 1
    ctx.strokeRect(overlayX + 10, yPos - indicatorSize/2, indicatorSize, indicatorSize)
    
    // Text (bold for dominant box)
    ctx.font = isDominant ? 'bold 11px Inter' : '11px Inter'
    ctx.fillStyle = isDominant ? '#ffffff' : '#e5e7eb'
    const text = `${box.label} ${Math.round(box.confidence * 100)}%`
    const coverage = `(${Math.round(box.intersectionArea * 100)}% visible)`
    
    ctx.fillText(text, overlayX + 30, yPos - 5)
    
    // Coverage percentage in smaller text
    ctx.font = '9px Inter'
    ctx.fillStyle = isDominant ? '#d1d5db' : '#9ca3af'
    ctx.fillText(coverage, overlayX + 30, yPos + 7)
    
    // Crown icon for dominant box
    if (isDominant) {
      ctx.fillStyle = '#fbbf24'
      ctx.font = '12px Arial'
      ctx.fillText('👑', overlayX + overlayWidth - 25, yPos)
    }
  })
  
  // Show count if there are more boxes
  if (magnifyingGlassBoxes.value.length > 6) {
    ctx.font = '10px Inter'
    ctx.fillStyle = '#9ca3af'
    ctx.fillText(`+${magnifyingGlassBoxes.value.length - 6} más...`, overlayX + 10, overlayY + overlayHeight - 10)
  }
}

const getColorForClass = (className) => {
  // Map class names back to colors
  const classMap = {
    'C5 DarkRed': '#991B1B',
    'C4 BrightRed': '#EF4444',
    'C3 Orange (Red dot)': '#F59E0B',
    'C2 Green': '#22C55E',
    'C1 Boton': '#6B7280'
  }
  return classMap[className] || '#6366F1'
}

const downloadResults = async () => {
  if (!result.value?.id) {
    console.error('No inference ID available for download')
    toast.error('No hay resultados disponibles para descargar')
    return
  }
  
  const apiUrl = import.meta.env.VITE_API_BASE_URL
  const inferenceId = result.value.id

  // Show loading state
  const downloadButton = document.querySelector('[data-download-button]')
  const originalText = downloadButton?.textContent
  if (downloadButton) {
    downloadButton.disabled = true
    downloadButton.textContent = 'Descargando...'
  }

  try {
    const response = await fetch(`${apiUrl}/inferences/${inferenceId}/download`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/zip, */*'
      }
    })
    
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Server error ${response.status}: ${errorText}`)
    }

    const contentType = response.headers.get('Content-Type')
    
    if (contentType && contentType.includes('text/html')) {
      const errorText = await response.text()
      if (errorText.includes('<div id="app"></div>') || errorText.includes('@vite/client')) {
        throw new Error('API backend is not accessible. Please check if the backend server is running on the correct port.')
      } else {
        throw new Error('Server returned an error page instead of the download file')
      }
    }
    
    if (contentType && contentType.includes('application/json')) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Server error occurred')
    }
    
    if (!contentType || (!contentType.includes('application/zip') && !contentType.includes('application/octet-stream'))) {
      throw new Error(`Unexpected response type: ${contentType}. Expected ZIP file.`)
    }

    const blob = await response.blob()
    
    if (blob.size === 0) {
      throw new Error('Downloaded file is empty')
    }
    
    if (blob.size < 100) {
      throw new Error('Downloaded file appears to be corrupted (too small)')
    }

    const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/zip' }))
    
    let filename = `inference_${inferenceId}_results.zip`
    const contentDisposition = response.headers.get('Content-Disposition')
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/i)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }
    
    if (!filename.toLowerCase().endsWith('.zip')) {
      filename += '.zip'
    }

    const downloadLink = document.createElement('a')
    downloadLink.href = url
    downloadLink.download = filename
    downloadLink.style.display = 'none'
    
    document.body.appendChild(downloadLink)
    downloadLink.click()
    
    setTimeout(() => {
      document.body.removeChild(downloadLink)
      window.URL.revokeObjectURL(url)
    }, 100)
    
    toast.success('Descarga iniciada correctamente. El archivo se guardará en tu carpeta de descargas.')
    
  } catch (error) {
    let errorMessage = 'Error al descargar los resultados.'
    if (error.message.includes('Server error')) {
      errorMessage += ' Error del servidor. Inténtalo de nuevo más tarde.'
    } else if (error.message.includes('empty') || error.message.includes('corrupted')) {
      errorMessage += ' El archivo descargado está dañado. Contacta al administrador.'
    } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
      errorMessage += ' Error de conexión. Verifica tu conexión a internet.'
    } else {
      errorMessage += ` Detalles: ${error.message}`
    }
    
    toast.error(errorMessage)
    
  } finally {
    // Restore button state
    if (downloadButton) {
      downloadButton.disabled = false
      downloadButton.textContent = originalText || 'Descargar Resultados'
    }
  }
}

const handleImageError = (event) => {
  event.target.src = '/frambuesas_1.jpg' // TODO: Add the fallback image
}
</script>

<style scoped>
/* --- ESTILOS BASE Y HEREDADOS --- */
:root {
  --primary-color: #b91c1c;
  --confirm-color: #16a34a;
  --accent-color: #6d28d9;
  --danger-color: #dc2626;
}
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 7rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #f9fafb;
}
.main-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.content-section {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07);
  padding: 2.5rem;
  text-align: center;
  border: 1px solid #e5e7eb;
}
.section-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #b22222;
  margin-bottom: 1.5rem;
}
.section-text {
  max-width: 800px;
  margin: -1rem auto 1.5rem auto;
  font-size: 1.1rem;
  line-height: 1.7;
  color: #555;
}

/* --- ESTILOS DE ENCABEZADO (HERO) --- */
.hero-section {
  background: linear-gradient(45deg, #b91c1c, #7f1d1d);
  color: white;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(185, 28, 28, 0.25);
}
.hero-title {
  font-size: 2.8rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.hero-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
  margin: 0 auto 1.5rem auto;
}
.user-badge {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.15);
  padding: 0.5rem 1.25rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* --- RESULTADOS: CONTENEDOR PRINCIPAL Y OVERLAY --- */
.results-section {
  background-color: #f0fdf4; /* Verde muy claro para la sección de resultados */
  border-color: #bbf7d0;
}
.results-image-wrapper {
  position: relative;
  background-color: #fff;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}
.loading-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  z-index: 30;
  border-radius: 12px;
  font-weight: 600;
  color: var(--confirm-color);
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--confirm-color);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* --- RESULTADOS: CONTROLES DE IMAGEN --- */
.image-controls-group {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.control-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background-color: #fff;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s ease;
}
.control-btn:hover:not(:disabled) {
  transform: scale(1.1);
  background-color: var(--primary-color);
  color: white;
}
.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* --- RESULTADOS: PANEL LATERAL DE CONTROLES --- */
.controls-panel-wrapper {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  z-index: 20;
}
.controls-panel {
  width: 48px;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  border: 1px solid #e5e7eb;
  transition: width 0.3s ease;
  overflow: hidden;
}
.controls-panel.is-expanded {
  width: 320px;
}
.panel-toggle-btn {
  width: 100%;
  padding: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
}
.panel-toggle-btn svg {
  width: 24px;
  height: 24px;
  stroke: #555;
  stroke-width: 2;
  fill: none;
  transition: transform 0.3s ease;
}
.controls-panel.is-expanded .panel-toggle-btn svg {
  transform: rotate(180deg);
}
.panel-content {
  padding: 0 1rem 1rem 1rem;
  border-top: 1px solid #e5e7eb;
}
.panel-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.panel-btn-small {
  flex: 1;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
}
.btn-confirm { background-color: var(--confirm-color); }
.btn-danger { background-color: var(--danger-color); }

/* --- RESULTADOS: LISTA DE CAJAS --- */
.box-list {
  max-height: 180px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.box-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: background-color 0.2s;
}
.box-list-item:hover {
  background-color: #f3f4f6;
}
.box-list-item.is-selected {
  background-color: #dbeafe;
  border-color: #93c5fd;
}
.box-info {
  flex: 1;
  min-width: 0;
}
.box-label {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.box-confidence {
  font-size: 0.8rem;
  color: #666;
}

/* --- RESULTADOS: CONTROLES DE LUPA --- */
.magnifying-glass-controls {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}
.magnifying-glass-controls .action-btn {
  width: 100%;
  padding: 0.6rem 1rem;
  font-size: 0.9rem;
  background: var(--accent-color);
}
.magnifying-glass-controls .action-btn.is-active {
  background: linear-gradient(45deg, #a855f7, #9333ea);
}
.magnifying-glass-settings {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  font-size: 0.9rem;
}
.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.setting-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.setting-actions button {
  width: 28px;
  height: 28px;
  border: 1px solid #ccc;
  background: #fff;
  border-radius: 5px;
  cursor: pointer;
}
.setting-actions span {
  font-weight: 600;
  min-width: 40px;
  text-align: center;
}
.panel-help-text {
  font-size: 0.8rem;
  color: #666;
  text-align: center;
  margin-top: 1rem;
}
.shortcuts p {
    margin: 0.25rem 0;
}
kbd {
  background-color: #e5e7eb;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 2px 5px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
}

/* --- RESULTADOS: CANVAS Y CURSORES --- */
.canvas-container {
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.result-image, .results-canvas {
  max-width: 100%;
  max-height: 600px;
  object-fit: contain;
  border-radius: 8px;
}
.results-canvas.cursor-crosshair { cursor: crosshair; }
.results-canvas.cursor-none { cursor: none; }
</style>
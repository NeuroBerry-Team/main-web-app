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
        <p v-if="user?.role" class="inline-block break-words bg-green-50 px-3 py-2 sm:px-5 sm:py-3 rounded-lg text-green-700 font-medium text-xs sm:text-sm lg:text-base mt-2 lg:mt-4">
          Conectado como: <strong>{{ user.role }}</strong>
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
      <section v-if="result" class="bg-gradient-to-br from-green-50 to-emerald-100 border-2 border-green-300 rounded-lg sm:rounded-xl lg:rounded-2xl p-4 sm:p-6 lg:p-8 text-center flex flex-col gap-4 sm:gap-6 lg:gap-8 shadow-xl">
        <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-green-800">Resultado del Análisis</h2>
        
        <!-- Image and controls container -->
        <div class="flex flex-col gap-4 sm:gap-6">
          <!-- Image display with loading state -->
          <div class="relative">
            <div v-if="metadataLoading" class="absolute inset-0 bg-white/80 rounded-lg flex items-center justify-center z-10">
              <div class="flex flex-col items-center gap-2">
                <div class="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div>
                <p class="text-sm text-green-700 font-medium">Cargando análisis...</p>
              </div>
            </div>
            
            <!-- Display the appropriate image based on box control mode -->
            <div style="position: relative; width: 100%; min-height: 256px; display: flex; align-items: center; justify-content: center;">
              <!-- Hidden image for canvas drawing - always loaded -->
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
                class="max-w-full max-h-64 sm:max-h-80 lg:max-h-96 mx-auto rounded-lg shadow-lg object-contain"
                style="display: block; width: 100%; height: 256px; object-fit: contain;"
              />
              <!-- Show canvas (image + boxes) in box control mode -->
              <canvas 
                v-if="showBoxControls && currentResultImage"
                ref="imageCanvas"
                class="max-w-full h-64 sm:h-80 lg:h-96 mx-auto rounded-lg shadow-lg border border-green-300"
                :class="{ 
                  'cursor-crosshair': !magnifyingGlassActive, 
                  'cursor-none': magnifyingGlassActive 
                }"
                style="display: block; width: 100%; height: 256px;"
                @click="handleCanvasClick"
                @dblclick="handleCanvasDoubleClick"
                @mousemove="handleCanvasMouseMove"
                @mouseleave="handleCanvasMouseLeave"
              ></canvas>
            </div>
          </div>

          <!-- Control buttons -->
          <div class="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full max-w-md mx-auto">
            <button 
              @click="toggleBoxControls"
              :disabled="metadataLoading || !detectedBoxes.length"
              class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-blue-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-blue-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <span v-if="!showBoxControls">🔍 Controles de Cajas</span>
              <span v-else>👁️ Ver Resultado</span>
            </button>
            <button 
              @click="startNewAnalysis"
              class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-green-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-green-700 transition-all duration-300 flex items-center justify-center gap-2"
            >
              🔄 Nuevo Análisis
            </button>
          </div>

          <!-- Magnifying glass controls (show when box controls are active) -->
          <div v-if="showBoxControls && detectedBoxes.length > 0" class="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full max-w-md mx-auto">
            <button 
              @click="toggleMagnifyingGlass"
              :class="[
                'flex-1 px-4 py-2 sm:px-6 sm:py-3 text-white text-sm sm:text-base font-bold rounded-lg transition-all duration-300 flex items-center justify-center gap-2',
                magnifyingGlassActive 
                  ? 'bg-purple-600 hover:bg-purple-700' 
                  : 'bg-indigo-600 hover:bg-indigo-700'
              ]"
            >
              <span v-if="!magnifyingGlassActive">🔍 Lupa</span>
              <span v-else>🔍 Salir de Lupa</span>
            </button>
            
            <!-- Zoom controls when magnifying glass is active -->
            <div v-if="magnifyingGlassActive" class="flex gap-2">
              <button 
                @click="magnifyingGlassZoom = Math.max(1.0, magnifyingGlassZoom - 0.1)"
                class="px-3 py-2 bg-gray-600 text-white text-sm font-bold rounded-lg hover:bg-gray-700 transition-all duration-300"
                :disabled="magnifyingGlassZoom <= 1.0"
              >
                🔍-
              </button>
              <span class="px-3 py-2 bg-gray-100 text-gray-800 text-sm font-medium rounded-lg flex items-center">
                {{ magnifyingGlassZoom.toFixed(1) }}x
              </span>
              <button 
                @click="magnifyingGlassZoom = Math.min(5.0, magnifyingGlassZoom + 0.1)"
                class="px-3 py-2 bg-gray-600 text-white text-sm font-bold rounded-lg hover:bg-gray-700 transition-all duration-300"
                :disabled="magnifyingGlassZoom >= 5.0"
              >
                🔍+
              </button>
            </div>
          </div>

          <!-- Size controls when magnifying glass is active -->
          <div v-if="showBoxControls && magnifyingGlassActive" class="flex gap-2 w-full max-w-md mx-auto">
            <span class="px-3 py-2 bg-gray-100 text-gray-800 text-xs font-medium rounded-lg flex items-center">
              Tamaño:
            </span>
            <button 
              @click="magnifyingGlassRadius = Math.max(30, magnifyingGlassRadius - 10)"
              class="px-3 py-2 bg-indigo-600 text-white text-sm font-bold rounded-lg hover:bg-indigo-700 transition-all duration-300"
              :disabled="magnifyingGlassRadius <= 30"
            >
              ◯-
            </button>
            <span class="px-3 py-2 bg-gray-100 text-gray-800 text-sm font-medium rounded-lg flex items-center min-w-[60px] justify-center">
              {{ Math.round(adaptiveMagnifyingGlassRadius) }}px
            </span>
            <button 
              @click="magnifyingGlassRadius = Math.min(80, magnifyingGlassRadius + 10)"
              class="px-3 py-2 bg-indigo-600 text-white text-sm font-bold rounded-lg hover:bg-indigo-700 transition-all duration-300"
              :disabled="magnifyingGlassRadius >= 80"
            >
              ◯+
            </button>
          </div>

          <!-- Help text for magnifying glass -->
          <p v-if="showBoxControls && magnifyingGlassActive" class="text-xs text-purple-600 text-center font-medium">
            Mueve el mouse sobre la imagen para usar la lupa. La información de las cajas se muestra en el borde y overlay.
          </p>

          <!-- Box controls panel (visible when box controls are active) -->
          <div v-if="showBoxControls && detectedBoxes.length > 0" class="bg-white/90 rounded-lg p-4 border border-green-200 shadow-inner">
            <div class="flex flex-col gap-4">
              <!-- Box visibility controls -->
              <div class="flex flex-col sm:flex-row gap-2 sm:gap-4">
                <h3 class="text-base font-semibold text-gray-800 sm:self-center">Control de Cajas:</h3>
                <div class="flex gap-2">
                  <button 
                    @click="toggleAllBoxes(true)"
                    class="px-3 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                  >
                    Mostrar Todas
                  </button>
                  <button 
                    @click="toggleAllBoxes(false)"
                    class="px-3 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                  >
                    Ocultar Todas
                  </button>
                </div>
              </div>

              <!-- Individual box controls -->
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 max-h-48 overflow-y-auto">
                <div 
                  v-for="box in detectedBoxes" 
                  :key="box.id"
                  class="flex items-center justify-between p-2 rounded border text-xs"
                  :class="{
                    'bg-blue-50 border-blue-300': selectedBox === box,
                    'bg-gray-50 border-gray-200': selectedBox !== box
                  }"
                >
                  <div class="flex items-center gap-2 flex-1 min-w-0">
                    <div 
                      class="w-3 h-3 rounded-sm border border-gray-400 flex-shrink-0"
                      :style="{ backgroundColor: box.color }"
                    ></div>
                    <span class="font-medium truncate" :style="{ color: box.color }">
                      {{ box.label }}
                    </span>
                    <span class="text-gray-600 flex-shrink-0">
                      {{ Math.round(box.confidence * 100) }}%
                    </span>
                  </div>
                  <button 
                    @click="selectBox(box)"
                    :class="[
                      'ml-2 px-2 py-1 text-xs rounded transition-colors flex-shrink-0',
                      selectedBox === box 
                        ? 'bg-blue-500 text-white hover:bg-blue-600' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    ]"
                  >
                    {{ selectedBox === box ? 'Deseleccionar' : 'Seleccionar' }}
                  </button>
                  <label class="flex items-center ml-2 flex-shrink-0">
                    <input 
                      type="checkbox" 
                      v-model="box.visible"
                      @change="updateImageWithBoxes"
                      class="w-3 h-3"
                    />
                  </label>
                </div>
              </div>
              
              <!-- Help text -->
              <p class="text-xs text-gray-600 text-center">
                Haz clic en una caja para seleccionarla, doble clic para mostrar/ocultar
              </p>
            </div>
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
            class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-indigo-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-indigo-700 transition-all duration-300 flex items-center justify-center gap-2"
          >
            💾 Descargar Resultados
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useAuth } from '../../composables/use_auth.js'
import { useInference } from '../../composables/send_inference.js'
import { useMinioMetadata } from '../../composables/use_minio_metadata.js'
import { useModels } from '../../composables/use_models.js'

// Authentication
const { isLoggedIn, user, loading: authLoading, checkAuthStatus } = useAuth()

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
const imageCanvas = ref(null)
const hiddenImage = ref(null)
const canvasContext = ref(null)
const canvasImageBounds = ref(null)

// Magnifying glass controls
const magnifyingGlassActive = ref(false)
const magnifyingGlassRadius = ref(50) // Smaller default radius
const magnifyingGlassPosition = ref({ x: 0, y: 0 })
const magnifyingGlassZoom = ref(1.0) // Zoom factor
const magnifyingGlassBoxes = ref([]) // Boxes within magnifying glass area

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
  const zoomAdjustedRadius = baseRadius * (1.5 / magnifyingGlassZoom.value)
  
  // Ensure minimum and maximum bounds
  return Math.max(25, Math.min(zoomAdjustedRadius, 120))
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
})

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
    alert('Por favor selecciona un archivo de imagen válido (JPG, PNG, WebP)')
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
    alert('Por favor selecciona una imagen primero')
    return
  }
  
  if (!isLoggedIn.value) {
    alert('Debes iniciar sesión para usar esta funcionalidad')
    return
  }

  if (!selectedModel.value) {
    alert('Por favor selecciona un modelo primero')
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
  const radius = adaptiveMagnifyingGlassRadius.value
  const bounds = canvasImageBounds.value
  
  if (!bounds) {
    magnifyingGlassBoxes.value = []
    return
  }
  
  magnifyingGlassBoxes.value = detectedBoxes.value.filter(box => {
    if (!box.visible || !box.bbox_normalized) return false
    
    const { x1, y1, x2, y2 } = box.bbox_normalized
    
    // Convert normalized coordinates to canvas coordinates
    const canvasX1 = x1 * bounds.drawWidth + bounds.drawX
    const canvasY1 = y1 * bounds.drawHeight + bounds.drawY
    const canvasX2 = x2 * bounds.drawWidth + bounds.drawX
    const canvasY2 = y2 * bounds.drawHeight + bounds.drawY
    
    // Calculate box dimensions
    const boxLeft = Math.min(canvasX1, canvasX2)
    const boxRight = Math.max(canvasX1, canvasX2)
    const boxTop = Math.min(canvasY1, canvasY2)
    const boxBottom = Math.max(canvasY1, canvasY2)
    const boxWidth = boxRight - boxLeft
    const boxHeight = boxBottom - boxTop
    
    // Add padding to exclude label areas - typically labels are at the top of boxes
    // Remove label area (approximately 20px or 15% of box height, whichever is smaller)
    const labelHeight = Math.min(20, boxHeight * 0.15)
    const paddingX = Math.min(4, boxWidth * 0.05)  // Small horizontal padding
    const paddingY = Math.min(4, boxHeight * 0.05) // Small vertical padding
    
    // Apply padding to create the "visible content area" (what user actually sees in magnifying glass)
    const contentLeft = boxLeft + paddingX
    const contentRight = boxRight - paddingX
    const contentTop = boxTop + labelHeight + paddingY // Exclude label area at top
    const contentBottom = boxBottom - paddingY
    
    // Only consider the content area for intersection calculation
    if (contentLeft >= contentRight || contentTop >= contentBottom) {
      // Box is too small after padding, skip it
      box.intersectionArea = 0
      return false
    }
    
    // Calculate intersection area with the circle using only the content area
    const intersectionArea = calculateBoxCircleIntersection(
      contentLeft, contentTop, contentRight, contentBottom,
      centerX, centerY, radius
    )
    
    // Store the intersection area for proportional border segments
    box.intersectionArea = intersectionArea
    
    return intersectionArea > 0
  }).sort((a, b) => b.intersectionArea - a.intersectionArea) // Sort by area, largest first
}

const calculateBoxCircleIntersection = (boxLeft, boxTop, boxRight, boxBottom, centerX, centerY, radius) => {
  // Simplified approach: sample points within the box and count how many are inside the circle
  const sampleSize = 20 // 20x20 grid for reasonable accuracy
  let pointsInside = 0
  let totalPoints = 0
  
  const stepX = (boxRight - boxLeft) / sampleSize
  const stepY = (boxBottom - boxTop) / sampleSize
  
  for (let i = 0; i < sampleSize; i++) {
    for (let j = 0; j < sampleSize; j++) {
      const x = boxLeft + i * stepX + stepX / 2
      const y = boxTop + j * stepY + stepY / 2
      
      const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2))
      if (distance <= radius) {
        pointsInside++
      }
      totalPoints++
    }
  }
  
  // Return the proportion of the box that's inside the circle
  return totalPoints > 0 ? pointsInside / totalPoints : 0
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

  // Get the actual container dimensions
  const containerRect = canvas.parentElement.getBoundingClientRect()
  const containerWidth = containerRect.width
  const containerHeight = 256 // h-64 class = 256px
  
  // Set canvas size to match the display size
  canvas.width = containerWidth
  canvas.height = containerHeight
  canvas.style.width = `${containerWidth}px`
  canvas.style.height = `${containerHeight}px`

  // Configure canvas context for better rendering
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'

  // Calculate object-contain bounds for the image
  const canvasAspectRatio = containerWidth / containerHeight
  const imageAspectRatio = img.naturalWidth / img.naturalHeight
  
  let drawWidth, drawHeight, drawX, drawY
  
  if (imageAspectRatio > canvasAspectRatio) {
    // Image is wider than container - fit to width
    drawWidth = containerWidth
    drawHeight = drawWidth / imageAspectRatio
    drawX = 0
    drawY = (containerHeight - drawHeight) / 2
  } else {
    // Image is taller than container - fit to height
    drawHeight = containerHeight
    drawWidth = drawHeight * imageAspectRatio
    drawX = (containerWidth - drawWidth) / 2
    drawY = 0
  }
  
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
      const cornerOffset = 12
      const corners = [
        { x: centerX + radius - cornerOffset, y: centerY - radius + cornerOffset }, // Top-right
        { x: centerX + radius - cornerOffset, y: centerY + radius - cornerOffset }, // Bottom-right
        { x: centerX - radius + cornerOffset, y: centerY + radius - cornerOffset }, // Bottom-left
        { x: centerX - radius + cornerOffset, y: centerY - radius + cornerOffset }  // Top-left
      ]
      
      // Show up to 4 additional boxes in corners
      magnifyingGlassBoxes.value.slice(1, 5).forEach((box, index) => {
        const corner = corners[index]
        if (corner) {
          // Draw small colored square indicator
          ctx.fillStyle = box.color
          ctx.fillRect(
            corner.x - indicatorSize / 2, 
            corner.y - indicatorSize / 2, 
            indicatorSize, 
            indicatorSize
          )
          
          // Add white border to indicator for better visibility
          ctx.strokeStyle = 'white'
          ctx.lineWidth = 1
          ctx.strokeRect(
            corner.x - indicatorSize / 2, 
            corner.y - indicatorSize / 2, 
            indicatorSize, 
            indicatorSize
          )
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

const downloadResults = () => {
  // TODO: Implement download functionality
  console.log('Download functionality not yet implemented')
  alert('Funcionalidad de descarga próximamente disponible')
}

const handleImageError = (event) => {
  event.target.src = '/frambuesas_1.jpg' // Fallback image
}
</script>

<style scoped>
.loading-spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #dc2626;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.gallery-item {
  transition: box-shadow 0.2s ease, transform 0.2s ease;
  will-change: box-shadow, transform;
}

.gallery-item:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

.gallery-item img {
  transition: transform 0.2s ease;
  will-change: transform;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

/* Canvas cursor styles */
canvas {
  transition: cursor 0.2s ease;
}

canvas:hover {
  cursor: pointer;
}

/* Magnifying glass cursor styles */
canvas.cursor-none {
  cursor: none;
}

/* Enhanced magnifying glass overlay styling */
.magnifying-overlay {
  pointer-events: none;
  font-family: 'Inter', system-ui, sans-serif;
}

/* Scrollbar styling for box controls */
.max-h-48::-webkit-scrollbar {
  width: 6px;
}

.max-h-48::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.max-h-48::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.max-h-48::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Enhanced button transitions */
button {
  transition: all 0.3s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

/* Enhanced card styling */
.bg-gradient-to-br {
  background-attachment: fixed;
}

/* Loading overlay styling */
.absolute.inset-0 {
  backdrop-filter: blur(2px);
}
</style>
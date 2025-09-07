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
            :disabled="loading" 
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
      <section v-if="error" class="bg-red-50 border-2 border-red-300 rounded-lg sm:rounded-xl p-4 sm:p-6 lg:p-8 text-center flex flex-col gap-4 sm:gap-6 lg:gap-8">
        <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-red-800">Error:</h2>
        <p class="text-red-700 font-medium text-sm sm:text-base mb-2 sm:mb-4 px-2">{{ error }}</p>
        <button v-if="error.includes('login')" 
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
                class="max-w-full h-64 sm:h-80 lg:h-96 mx-auto rounded-lg shadow-lg cursor-crosshair border border-green-300"
                style="display: block; width: 100%; height: 256px;"
                @click="handleCanvasClick"
                @dblclick="handleCanvasDoubleClick"
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

// Box controls
const showBoxControls = ref(false)
const selectedBox = ref(null)
const imageCanvas = ref(null)
const hiddenImage = ref(null)
const canvasContext = ref(null)
const canvasImageBounds = ref(null)

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

// Watch for result changes to fetch metadata
watch(result, async (newResult) => {
  if (newResult && newResult.id) {
    await fetchMetadata(newResult.id)
  }
}, { immediate: true })

// Check auth status on mount
onMounted(() => {
  checkAuthStatus()
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

  await handleInference(selectedFile.value)
}

function startNewAnalysis() {
  resetImage()
  result.value = null
  showBoxControls.value = false
  selectedBox.value = null
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

  // Get visible boxes with normalized coordinates
  const visibleBoxes = detectedBoxes.value.filter(box => box.visible && box.bbox_normalized)
  
  if (visibleBoxes.length === 0) {
    return
  }

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
  
  const canvas = imageCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = (event.clientX - rect.left) * (canvas.width / rect.width)
  const y = (event.clientY - rect.top) * (canvas.height / rect.height)
  
  const clickedBox = findBoxAtPosition(x, y)
  selectBox(clickedBox)
}

const handleCanvasDoubleClick = (event) => {
  if (!showBoxControls.value || !canvasContext.value || !imageCanvas.value) return
  
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
  cursor: crosshair;
}

canvas:hover {
  cursor: pointer;
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
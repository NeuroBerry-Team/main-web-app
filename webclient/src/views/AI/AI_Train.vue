<template>
  <div class="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
    <!-- Access denied for non-admin users -->
    <section v-if="!isLoggedIn || !isAdmin" class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-red-50 to-red-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl">
      <div class="text-center">
        <div class="text-6xl mb-4">🔒</div>
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-red-700 mb-4">Acceso Restringido</h1>
        <p class="text-lg text-gray-600 mb-6">
          Esta sección está disponible solo para administradores y superadministradores.
        </p>
        <router-link 
          v-if="!isLoggedIn"
          to="/login" 
          class="inline-block px-6 py-3 bg-red-700 text-white font-bold rounded-lg hover:bg-red-800 transition-all duration-300"
        >
          Iniciar Sesión
        </router-link>
      </div>
    </section>

    <!-- Loading authentication -->
    <section v-if="authLoading" class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-slate-50 to-blue-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl">
      <h1 class="text-xl sm:text-2xl lg:text-4xl font-extrabold text-red-700">Verificando autenticación...</h1>
    </section>

    <!-- Main content - only show if authenticated and admin -->
    <div v-if="isLoggedIn && isAdmin && !authLoading" class="space-y-6">
      <!-- Header -->
      <section class="p-6 bg-gradient-to-br from-purple-50 to-indigo-100 rounded-xl shadow-lg">
        <h1 class="text-3xl font-extrabold text-purple-700 mb-2">🏋️ Entrenamiento de Modelos IA</h1>
        <p class="text-gray-600">
          Configura y entrena modelos de inteligencia artificial usando YOLOv8 con tus datasets personalizados.
        </p>
        <div class="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-3">
          <p class="text-sm text-purple-700">
            <strong>Conectado como:</strong> {{ user?.role }}
          </p>
        </div>
      </section>

      <!-- Training Configuration Form -->
      <section class="bg-white rounded-xl shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Configuración de Entrenamiento</h2>
        
        <form @submit.prevent="handleTraining" class="space-y-6">
          <!-- Dataset Selection -->
          <div class="space-y-3">
            <label class="block text-sm font-bold text-gray-700">
              Dataset <span class="text-red-500">*</span>
            </label>
            <select 
              v-model.number="trainingConfig.datasetId" 
              required
              :disabled="isTraining"
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
            >
              <option :value="null">Selecciona un dataset</option>
              <option 
                v-for="dataset in availableDatasets" 
                :key="dataset.id" 
                :value="dataset.id"
              >
                {{ dataset.name }} - {{ dataset.description || 'Sin descripción' }}
              </option>
            </select>
            <p class="text-sm text-gray-500">
              Selecciona el dataset que se utilizará para entrenar el modelo.
            </p>
          </div>

          <!-- Model Configuration -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Model Type -->
            <div class="space-y-3">
              <label class="block text-sm font-bold text-gray-700">
                Tipo de Modelo
              </label>
              <select 
                v-model="trainingConfig.modelType" 
                :disabled="isTraining"
                class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
              >
                <option value="YOLOv8_m">YOLOv8 Medium (Recomendado)</option>
              </select>
              <p class="text-sm text-gray-500">
                Por ahora solo disponible YOLOv8 Medium. Más opciones próximamente.
              </p>
            </div>

            <!-- Model Name -->
            <div class="space-y-3">
              <label class="block text-sm font-bold text-gray-700">
                Nombre del Modelo <span class="text-red-500">*</span>
              </label>
              <input 
                v-model="trainingConfig.modelName" 
                type="text" 
                required
                :disabled="isTraining"
                placeholder="Ej: FrambuesiasModel_v1"
                class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
              />
              <p class="text-sm text-gray-500">
                Nombre único para identificar tu modelo.
              </p>
            </div>
          </div>

          <!-- Training Parameters -->
          <div class="bg-gray-50 rounded-xl p-6 space-y-6">
            <h3 class="text-lg font-bold text-gray-800">Parámetros de Entrenamiento</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <!-- Epochs -->
              <div class="space-y-3">
                <label class="block text-sm font-bold text-gray-700">
                  Épocas
                </label>
                <input 
                  v-model.number="trainingConfig.epochs" 
                  type="number" 
                  min="1" 
                  max="1000"
                  :disabled="isTraining"
                  class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
                />
                <p class="text-sm text-gray-500">
                  <strong>Recomendado:</strong> 50-100 para datasets pequeños, 20-50 para datasets grandes.
                </p>
              </div>

              <!-- Image Size -->
              <div class="space-y-3">
                <label class="block text-sm font-bold text-gray-700">
                  Tamaño de Imagen
                </label>
                <select 
                  v-model.number="trainingConfig.imageSize" 
                  :disabled="isTraining"
                  class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
                >
                  <option :value="416">416x416</option>
                  <option :value="512">512x512</option>
                  <option :value="640">640x640 (Recomendado)</option>
                  <option :value="800">800x800</option>
                </select>
                <p class="text-sm text-gray-500">
                  <strong>Recomendado:</strong> 640x640 para mejor precisión/velocidad.
                </p>
              </div>

              <!-- Batch Size -->
              <div class="space-y-3">
                <label class="block text-sm font-bold text-gray-700">
                  Tamaño de Lote
                </label>
                <select 
                  v-model.number="trainingConfig.batchSize" 
                  :disabled="isTraining"
                  class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
                >
                  <option :value="8">8</option>
                  <option :value="16">16 (Recomendado)</option>
                  <option :value="32">32</option>
                  <option :value="64">64</option>
                </select>
                <p class="text-sm text-gray-500">
                  <strong>Recomendado:</strong> 16 para la mayoría de casos. Usar valores menores si hay problemas de memoria.
                </p>
              </div>
            </div>

            <!-- Advanced Options -->
            <div class="space-y-4">
              <h4 class="text-md font-semibold text-gray-700">Opciones Avanzadas</h4>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Learning Rate -->
                <div class="space-y-3">
                  <label class="block text-sm font-bold text-gray-700">
                    Tasa de Aprendizaje
                  </label>
                  <input 
                    v-model.number="trainingConfig.learningRate" 
                    type="number" 
                    step="0.0001"
                    min="0.0001"
                    max="0.1"
                    :disabled="isTraining"
                    class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
                  />
                  <p class="text-sm text-gray-500">
                    <strong>Recomendado:</strong> 0.01 para la mayoría de casos.
                  </p>
                </div>

                <!-- Patience -->
                <div class="space-y-3">
                  <label class="block text-sm font-bold text-gray-700">
                    Paciencia (Early Stopping)
                  </label>
                  <input 
                    v-model.number="trainingConfig.patience" 
                    type="number" 
                    min="5"
                    max="100"
                    :disabled="isTraining"
                    class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50"
                  />
                  <p class="text-sm text-gray-500">
                    <strong>Recomendado:</strong> 20-30 épocas sin mejora antes de parar.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="space-y-3">
            <label class="block text-sm font-bold text-gray-700">
              Descripción del Modelo
            </label>
            <textarea 
              v-model="trainingConfig.description" 
              rows="3"
              :disabled="isTraining"
              placeholder="Describe brevemente este modelo y su propósito..."
              class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-300 disabled:bg-gray-50 resize-none"
            ></textarea>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end space-x-4">
            <button 
              type="button" 
              @click="resetForm"
              :disabled="isTraining"
              class="px-6 py-3 border-2 border-gray-300 text-gray-700 font-bold rounded-xl hover:bg-gray-50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Limpiar Formulario
            </button>
            <button 
              type="submit" 
              :disabled="isTraining || !isFormValid"
              class="px-8 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white font-bold rounded-xl hover:from-purple-700 hover:to-purple-800 transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
            >
              <span v-if="isTraining" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>{{ isTraining ? 'Iniciando Entrenamiento...' : 'Iniciar Entrenamiento' }}</span>
            </button>
          </div>
        </form>
      </section>

      <!-- Error Display -->
      <section v-if="error" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-xl shadow-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
              <span class="text-white text-sm font-bold">!</span>
            </div>
          </div>
          <div class="ml-3">
            <h3 class="text-red-700 font-bold">Error</h3>
            <p class="text-red-600">{{ error }}</p>
          </div>
        </div>
      </section>

      <!-- Success Display -->
      <section v-if="successMessage" class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-xl shadow-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <span class="text-white text-sm font-bold">✓</span>
            </div>
          </div>
          <div class="ml-3">
            <h3 class="text-green-700 font-bold">¡Éxito!</h3>
            <p class="text-green-600">{{ successMessage }}</p>
          </div>
        </div>
      </section>

      <!-- Training Info -->
      <section class="bg-blue-50 rounded-xl p-6">
        <h3 class="text-lg font-bold text-blue-800 mb-4">ℹ️ Información Importante</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-white rounded-lg p-4">
            <h4 class="font-semibold text-blue-700 mb-2">Tiempo de Entrenamiento</h4>
            <p class="text-sm text-gray-600">
              El tiempo depende del tamaño del dataset y parámetros. Puede tomar desde minutos hasta horas.
            </p>
          </div>
          <div class="bg-white rounded-lg p-4">
            <h4 class="font-semibold text-blue-700 mb-2">Proceso Asíncrono</h4>
            <p class="text-sm text-gray-600">
              El entrenamiento se ejecuta en segundo plano. Recibirás notificaciones del progreso.
            </p>
          </div>
          <div class="bg-white rounded-lg p-4">
            <h4 class="font-semibold text-blue-700 mb-2">Registro de Auditoría</h4>
            <p class="text-sm text-gray-600">
              Todas las acciones de entrenamiento se registran para seguimiento y auditoría.
            </p>
          </div>
          <div class="bg-white rounded-lg p-4">
            <h4 class="font-semibold text-blue-700 mb-2">Almacenamiento Automático</h4>
            <p class="text-sm text-gray-600">
              Los modelos entrenados se guardan automáticamente en el sistema de archivos.
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '../../composables/use_auth.js'
import { useCSRF } from '../../composables/use_csrf.js'
import { useAudit } from '../../composables/log_audit.js'

// Composables
const { isLoggedIn, isAdmin, user, loading: authLoading, checkAuthStatus } = useAuth()
const { makeSecureRequest } = useCSRF()
const { logModelTraining } = useAudit()

// API URL
const apiUrl = import.meta.env.VITE_API_BASE_URL

// State
const availableDatasets = ref([])
const isTraining = ref(false)
const error = ref('')
const successMessage = ref('')
const loadingDatasets = ref(false)

// Training configuration
const trainingConfig = ref({
  datasetId: null,
  modelName: '',
  modelType: 'YOLOv8_m',
  description: '',
  epochs: 50,
  imageSize: 640,
  batchSize: 16,
  learningRate: 0.01,
  patience: 30
})

// Computed properties
const isFormValid = computed(() => {
  const datasetId = trainingConfig.value.datasetId
  const isValid = datasetId !== null && 
         datasetId !== '' &&
         Number.isInteger(datasetId) &&
         datasetId > 0 &&
         trainingConfig.value.modelName.trim().length > 0 &&
         trainingConfig.value.epochs > 0 &&
         trainingConfig.value.batchSize > 0 &&
         trainingConfig.value.learningRate > 0
  
  // Debug logging
  console.log('Form validation debug:', {
    datasetId,
    datasetIdType: typeof datasetId,
    datasetIdValid: datasetId !== null && datasetId !== '' && Number.isInteger(datasetId) && datasetId > 0,
    modelNameValid: trainingConfig.value.modelName.trim().length > 0,
    epochsValid: trainingConfig.value.epochs > 0,
    batchSizeValid: trainingConfig.value.batchSize > 0,
    learningRateValid: trainingConfig.value.learningRate > 0,
    overallValid: isValid
  })
  
  return isValid
})

// Methods
const fetchAvailableDatasets = async () => {
  // Get all datasets to show on the training page
  loadingDatasets.value = true
  error.value = ''
  
  try {
    const response = await makeSecureRequest(`${apiUrl}/datasets/`, {
      method: 'GET'
    })
    if (response.ok) {
      const data = await response.json()
      availableDatasets.value = data.datasets || []
    } else {
      console.error('Failed to fetch datasets')
    }
  } catch (err) {
    console.error('Error fetching datasets:', err)
  } finally {
    loadingDatasets.value = false
  }
}

const handleTraining = async () => {
  if (!isFormValid.value || isTraining.value) return

  isTraining.value = true
  error.value = ''
  successMessage.value = ''

  try {
    // Prepare training payload
    const trainingPayload = {
      datasetId: trainingConfig.value.datasetId, // Should already be an integer
      modelName: trainingConfig.value.modelName.trim(),
      modelType: trainingConfig.value.modelType,
      description: trainingConfig.value.description.trim(),
      trainingParams: {
        epochs: trainingConfig.value.epochs,
        imageSize: trainingConfig.value.imageSize,
        batchSize: trainingConfig.value.batchSize,
        learningRate: trainingConfig.value.learningRate,
        patience: trainingConfig.value.patience
      }
    }

    console.log('Training payload being sent:', trainingPayload)
    console.log('Dataset ID type:', typeof trainingConfig.value.datasetId)
    console.log('Dataset ID value:', trainingConfig.value.datasetId)

    const response = await makeSecureRequest(`${apiUrl}/models/train`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(trainingPayload)
    })

    console.log('Training request response:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    })

    if (response.ok) {
      const data = await response.json()
      
      successMessage.value = `¡Entrenamiento iniciado correctamente! ID del trabajo: ${data.jobId || 'N/A'}`
      
      // Log audit action
      await logModelTraining(
        trainingConfig.value.modelName,
        trainingConfig.value.datasetId,
        trainingConfig.value.modelType,
        data.modelId
      )
      
      // Reset form after successful submission
      setTimeout(() => {
        resetForm()
        successMessage.value = ''
      }, 5000)
      
    } else {
      // Handle error response properly
      try {
        const errorData = await response.json()
        error.value = errorData.message || `Error ${response.status}: ${response.statusText}`
        console.error('Training API error:', errorData)
      } catch (parseError) {
        error.value = `Error ${response.status}: ${response.statusText}`
        console.error('Training API error (no JSON):', response.statusText)
      }
    }

  } catch (err) {
    console.error('Error starting training:', err)
    error.value = 'Error al iniciar el entrenamiento. Por favor, inténtalo de nuevo.'
  } finally {
    isTraining.value = false
  }
}

const resetForm = () => {
  trainingConfig.value = {
    datasetId: null,
    modelName: '',
    modelType: 'YOLOv8_m',
    description: '',
    epochs: 50,
    imageSize: 640,
    batchSize: 16,
    learningRate: 0.01,
    patience: 30
  }
  error.value = ''
  successMessage.value = ''
}

onMounted(async () => {
  await checkAuthStatus()
  
  if (isLoggedIn.value && isAdmin.value) {
    await fetchAvailableDatasets()
  }
})
</script>
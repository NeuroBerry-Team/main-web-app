<template>
  <div class="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
    <!-- Header -->
    <section class="p-6 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl shadow-lg mb-6">
      <h1 class="text-3xl font-extrabold text-blue-700 mb-2">
        🔄 Gestión de Entrenamientos
      </h1>
      <p class="text-gray-600">
        {{ isSuperAdmin 
            ? 'Gestiona todos los trabajos de entrenamiento del sistema.' 
            : 'Gestiona tus trabajos de entrenamiento activos.' }}
      </p>
      <div class="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p class="text-sm text-blue-700">
          <strong>Conectado como:</strong> {{ user?.role }} 
          <span v-if="isSuperAdmin" class="text-orange-600 font-semibold"> 
            (Acceso completo)
          </span>
        </p>
      </div>
    </section>

    <!-- Filters and Controls -->
    <section class="bg-white rounded-xl shadow-lg p-6 mb-6">
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <!-- Status Filter -->
        <div class="flex flex-wrap gap-2">
          <button 
            v-for="status in statusFilters" 
            :key="status.value"
            @click="activeFilter = status.value"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-all duration-200',
              activeFilter === status.value 
                ? status.activeClass 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            ]"
          >
            {{ status.label }}
            <span v-if="getJobCountByStatus(status.value) > 0" 
                  class="ml-2 px-2 py-1 bg-white bg-opacity-30 rounded-full text-xs">
              {{ getJobCountByStatus(status.value) }}
            </span>
          </button>
        </div>

        <!-- Refresh Button -->
        <button 
          @click="refreshJobs"
          :disabled="isLoading"
          class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <span v-else>🔄</span>
          {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </section>

    <!-- Training Jobs List -->
    <section class="bg-white rounded-xl shadow-lg p-6">
      <div v-if="isLoading && trainingJobs.length === 0" class="text-center py-8">
        <div class="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-gray-600">Cargando trabajos de entrenamiento...</p>
      </div>

      <div v-else-if="filteredJobs.length === 0" class="text-center py-8">
        <div class="text-6xl mb-4">📝</div>
        <h3 class="text-xl font-bold text-gray-700 mb-2">No hay entrenamientos</h3>
        <p class="text-gray-500">
          {{ activeFilter === 'all' 
              ? 'No se encontraron trabajos de entrenamiento.' 
              : `No hay entrenamientos con estado "${getStatusLabel(activeFilter)}".` }}
        </p>
      </div>

      <div v-else class="space-y-4">
        <div 
          v-for="job in filteredJobs" 
          :key="job.jobId"
          class="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-all duration-200"
        >
          <!-- Job Header -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-bold text-gray-800">
                  {{ job.trainingData?.modelName || 'Modelo sin nombre' }}
                </h3>
                <span :class="getStatusBadgeClass(job.status)" class="px-3 py-1 rounded-full text-sm font-medium">
                  {{ getStatusLabel(job.status) }}
                </span>
              </div>
              <div class="flex flex-wrap gap-4 text-sm text-gray-600">
                <span><strong>ID:</strong> {{ job.jobId }}</span>
                <span><strong>Tipo:</strong> {{ job.trainingData?.modelType || 'N/A' }}</span>
                <span><strong>Creado:</strong> {{ formatDate(job.createdAt) }}</span>
                <span v-if="job.startedAt"><strong>Iniciado:</strong> {{ formatDate(job.startedAt) }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2">
              <button 
                @click="viewJobDetails(job)"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all duration-200"
              >
                👁️ Ver Detalles
              </button>
              
              <button 
                v-if="canCancelJob(job)"
                @click="confirmCancelJob(job)"
                :disabled="isCancelling[job.jobId]"
                class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="isCancelling[job.jobId]" class="w-4 h-4 border-2 border-red-700 border-t-transparent rounded-full animate-spin inline-block mr-1"></span>
                {{ isCancelling[job.jobId] ? 'Cancelando...' : '❌ Cancelar' }}
              </button>
            </div>
          </div>

          <!-- Progress Bar (for running jobs) -->
          <div v-if="job.status === 'running' && job.progress" class="mb-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-700">
                Progreso: {{ job.progress.stage || 'En proceso' }}
              </span>
              <span class="text-sm text-gray-500">
                {{ job.progress.percentage || 0 }}%
              </span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="`width: ${job.progress.percentage || 0}%`"
              ></div>
            </div>
          </div>

          <!-- Training Parameters -->
          <div v-if="job.trainingData?.trainingParams" class="bg-gray-50 rounded-lg p-4">
            <h4 class="font-semibold text-gray-700 mb-2">Parámetros de Entrenamiento</h4>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
              <div><strong>Épocas:</strong> {{ job.trainingData.trainingParams.epochs }}</div>
              <div><strong>Batch Size:</strong> {{ job.trainingData.trainingParams.batchSize }}</div>
              <div><strong>Learning Rate:</strong> {{ job.trainingData.trainingParams.learningRate }}</div>
              <div><strong>Paciencia:</strong> {{ job.trainingData.trainingParams.patience }}</div>
            </div>
          </div>

          <!-- Error Message (for failed jobs) -->
          <div v-if="job.status === 'failed' && job.errorMessage" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 class="font-semibold text-red-700 mb-2">❌ Error</h4>
            <p class="text-red-600 text-sm">{{ job.errorMessage }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Cancel Confirmation Modal -->
    <div v-if="showCancelModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click="showCancelModal = false">
      <div class="bg-white rounded-xl p-6 max-w-md mx-4" @click.stop>
        <h3 class="text-lg font-bold text-gray-800 mb-4">⚠️ Confirmar Cancelación</h3>
        <p class="text-gray-600 mb-6">
          ¿Estás seguro de que deseas cancelar el entrenamiento 
          <strong>{{ jobToCancel?.trainingData?.modelName }}</strong>?
          <br><br>
          Esta acción no se puede deshacer.
        </p>
        <div class="flex gap-3 justify-end">
          <button 
            @click="showCancelModal = false"
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button 
            @click="cancelJob"
            :disabled="isCancelling[jobToCancel?.jobId]"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isCancelling[jobToCancel?.jobId] ? 'Cancelando...' : 'Sí, Cancelar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuth } from '../../composables/use_auth.js'
import { useCSRF } from '../../composables/use_csrf.js'

// Composables
const { isLoggedIn, isAdmin, isSuperAdmin, user, checkAuthStatus } = useAuth()
const { makeSecureRequest } = useCSRF()

// Flask API URL
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// State
const trainingJobs = ref([])
const isLoading = ref(false)
const error = ref('')
const activeFilter = ref('all')
const showCancelModal = ref(false)
const jobToCancel = ref(null)
const isCancelling = ref({})
const refreshInterval = ref(null)

// Status filters configuration
const statusFilters = ref([
  { value: 'all', label: 'Todos', activeClass: 'bg-blue-100 text-blue-700' },
  { value: 'pending', label: 'Pendiente', activeClass: 'bg-yellow-100 text-yellow-700' },
  { value: 'running', label: 'Ejecutando', activeClass: 'bg-green-100 text-green-700' },
  { value: 'completed', label: 'Completado', activeClass: 'bg-emerald-100 text-emerald-700' },
  { value: 'failed', label: 'Fallido', activeClass: 'bg-red-100 text-red-700' },
  { value: 'cancelled', label: 'Cancelado', activeClass: 'bg-gray-100 text-gray-700' }
])

// Computed
const filteredJobs = computed(() => {
  if (activeFilter.value === 'all') return trainingJobs.value
  return trainingJobs.value.filter(job => job.status === activeFilter.value)
})

// Methods
const fetchTrainingJobs = async () => {
  try {
    isLoading.value = true
    error.value = ''

    const response = await makeSecureRequest(`${apiUrl}/models/training-jobs`, {
      method: 'GET'
    })

    if (response.ok) {
      const data = await response.json()
      console.log('Training jobs response:', data) // Debug log
      trainingJobs.value = data.jobs || []
      
      // Log active jobs for debugging
      const activeJobs = trainingJobs.value.filter(job => ['pending', 'running'].includes(job.status))
      if (activeJobs.length > 0) {
        console.log(`Found ${activeJobs.length} active training jobs`)
      }
    } else {
      const errorData = await response.json().catch(() => ({}))
      error.value = errorData.message || `Error ${response.status}: ${response.statusText}`
      console.error('Training jobs fetch error:', error.value)
    }
  } catch (err) {
    console.error('Error fetching training jobs:', err)
    error.value = 'Error al cargar los trabajos de entrenamiento'
  } finally {
    isLoading.value = false
  }
}

const refreshJobs = async () => {
  await fetchTrainingJobs()
}

const canCancelJob = (job) => {
  // Only pending or running jobs can be cancelled
  if (!['pending', 'running'].includes(job.status)) return false
  
  // Super admins can cancel any job
  if (isSuperAdmin.value) return true
  
  // Regular admins can only cancel their own jobs
  // Note: We'll need to add user tracking to jobs for this to work properly
  return true // For now, allow all admins to cancel
}

const confirmCancelJob = (job) => {
  jobToCancel.value = job
  showCancelModal.value = true
}

const cancelJob = async () => {
  if (!jobToCancel.value) return
  
  const jobId = jobToCancel.value.jobId
  isCancelling.value[jobId] = true
  
  try {
    const response = await makeSecureRequest(`${apiUrl}/models/training-jobs/${jobId}`, {
      method: 'DELETE'
    })

    if (response.ok) {
      showCancelModal.value = false
      jobToCancel.value = null
      await refreshJobs() // Refresh the list
    } else {
      const errorData = await response.json().catch(() => ({}))
      error.value = errorData.message || 'Error al cancelar el entrenamiento'
    }
  } catch (err) {
    console.error('Error cancelling job:', err)
    error.value = 'Error al cancelar el entrenamiento'
  } finally {
    isCancelling.value[jobId] = false
  }
}

const viewJobDetails = (job) => {
  // TODO: Implement detailed view modal or navigate to details page
  console.log('View job details:', job)
}

const getJobCountByStatus = (status) => {
  if (status === 'all') return trainingJobs.value.length
  return trainingJobs.value.filter(job => job.status === status).length
}

const getStatusLabel = (status) => {
  const filter = statusFilters.value.find(f => f.value === status)
  return filter ? filter.label : status
}

const getStatusBadgeClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    running: 'bg-green-100 text-green-800 border border-green-200',
    completed: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
    failed: 'bg-red-100 text-red-800 border border-red-200',
    cancelled: 'bg-gray-100 text-gray-800 border border-gray-200'
  }
  return classes[status] || 'bg-gray-100 text-gray-800 border border-gray-200'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Auto-refresh for running jobs
const startAutoRefresh = () => {
  refreshInterval.value = setInterval(async () => {
    const hasActiveJobs = trainingJobs.value.some(job => 
      ['pending', 'running'].includes(job.status)
    )
    
    if (hasActiveJobs && !isLoading.value) {
      // Only refresh if we're not already loading to avoid conflicts
      try {
        await fetchTrainingJobs()
      } catch (err) {
        console.error('Auto-refresh error:', err)
      }
    }
  }, 3000) // Refresh every 3 seconds for more responsive updates
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// Lifecycle
onMounted(async () => {
  await checkAuthStatus()
  
  if (isLoggedIn.value && isAdmin.value) {
    await fetchTrainingJobs()
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

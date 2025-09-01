<template>
  <!-- Modal Overlay -->
  <Teleport to="body">
    <div class="modal-overlay" @click.self="goBack">
      <div class="modal-container" @click.stop>
        <div class="bg-gradient-to-r from-indigo-600 via-indigo-700 to-indigo-800 text-white p-6 flex items-center justify-between relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12"></div>
          
          <div class="relative z-10 flex items-center space-x-3">
            <div class="text-2xl">📋</div>
            <div>
              <h2 class="text-2xl font-bold">Registro de Actividad</h2>
              <p class="text-indigo-100 mt-1">Historial de acciones y sesiones</p>
            </div>
          </div>
          
          <div class="relative z-10">
            <button 
              @click="goBack" 
              class="text-white hover:text-indigo-200 text-3xl font-light w-10 h-10 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-all duration-200 hover:rotate-90 transform"
              title="Cerrar ventana (ESC)"
            >
              ×
            </button>
          </div>
        </div>

        <div class="flex-1 p-8 overflow-y-auto bg-gray-50">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-12">
            <div class="text-4xl mb-4">⏳</div>
            <p class="text-gray-500">Cargando registro de actividad...</p>
          </div>
          
          <!-- Error State -->
          <div v-else-if="error" class="text-center py-12">
            <div class="text-4xl mb-4">❌</div>
            <p class="text-red-500 mb-4">Error al cargar el registro de actividad</p>
            <button 
              @click="loadActivityLogs"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
            >
              Intentar de nuevo
            </button>
          </div>
          
          <!-- Empty State -->
          <div v-else-if="!activityLogs.length" class="text-center py-12">
            <div class="text-6xl mb-6">📋</div>
            <h3 class="text-xl font-semibold text-gray-700 mb-2">No hay actividad registrada</h3>
            <p class="text-gray-500 mb-6">Tu actividad aparecerá aquí cuando realices acciones en la plataforma</p>
          </div>
          
          <!-- Activity Timeline -->
          <div v-else class="space-y-6">
            <!-- Activity Summary Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-green-100 rounded-lg">
                    <div class="text-2xl">🔓</div>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Inicios de sesión</p>
                    <p class="text-2xl font-bold text-gray-900">{{ loginCount }}</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-blue-100 rounded-lg">
                    <div class="text-2xl">🔬</div>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Análisis realizados</p>
                    <p class="text-2xl font-bold text-gray-900">{{ analysisCount }}</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-orange-100 rounded-lg">
                    <div class="text-2xl">📊</div>
                  </div>
                  <div class="ml-4">
                    <p class="text-sm font-medium text-gray-600">Total actividades</p>
                    <p class="text-2xl font-bold text-gray-900">{{ activityLogs.length }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Timeline -->
            <div class="space-y-6">
              <div 
                v-for="(activities, dateKey) in groupedActivities" 
                :key="dateKey"
                class="space-y-4"
              >
                <!-- Date Header -->
                <div class="flex items-center">
                  <h3 class="text-lg font-semibold text-gray-800">
                    {{ formatDateHeader(dateKey) }}
                  </h3>
                  <div class="flex-1 h-px bg-gray-300 ml-4"></div>
                </div>
                
                <!-- Activities for this date -->
                <div class="space-y-3">
                  <div
                    v-for="activity in activities"
                    :key="activity.id"
                    class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden border border-gray-200"
                  >
                    <div class="p-6">
                      <div class="flex items-start">
                        <!-- Activity Icon -->
                        <div class="flex-shrink-0">
                          <div :class="[activity.color, 'w-10 h-10 rounded-full flex items-center justify-center text-white text-lg']">
                            {{ activity.icon }}
                          </div>
                        </div>
                        
                        <!-- Activity Content -->
                        <div class="ml-4 flex-1">
                          <div class="flex items-start justify-between">
                            <div>
                              <h4 class="text-sm font-semibold text-gray-900">
                                {{ activity.title }}
                              </h4>
                              <p class="text-sm text-gray-600 mt-1">
                                {{ activity.subtitle }}
                              </p>
                            </div>
                            <div class="text-xs text-gray-500 ml-4">
                              {{ formatTime(activity.timestamp) }}
                            </div>
                          </div>
                          
                          <!-- Activity Details -->
                          <div v-if="activity.details" class="mt-3 space-y-1">
                            <div 
                              v-for="(value, key) in activity.details" 
                              :key="key"
                              class="flex justify-between items-center text-xs"
                            >
                              <span class="text-gray-500 capitalize">{{ key }}:</span>
                              <span class="text-gray-700 font-mono">{{ value }}</span>
                            </div>
                          </div>
                          
                          <!-- Activity Type Badge -->
                          <div class="mt-3">
                            <span 
                              :class="getActivityBadgeClass(activity.type)"
                              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                            >
                              {{ getActivityTypeLabel(activity.type) }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Load More Button -->
            <div v-if="hasMore && !loading" class="text-center mt-8">
              <button
                @click="loadMoreLogs"
                class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors duration-200"
              >
                Cargar más actividades
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activityLogs = ref([])
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
    goBack()
  }
}

// Group activities by date
const groupedActivities = computed(() => {
  if (!activityLogs.value.length) return {}
  
  const groups = {}
  activityLogs.value.forEach(activity => {
    const dateKey = activity.timestamp.toDateString()
    if (!groups[dateKey]) {
      groups[dateKey] = []
    }
    groups[dateKey].push(activity)
  })
  
  // Sort each group by time (newest first)
  Object.keys(groups).forEach(date => {
    groups[date].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  })
  
  return groups
})

// Activity statistics
const loginCount = computed(() => {
  return activityLogs.value.filter(activity => activity.type === 'login').length
})

const analysisCount = computed(() => {
  return activityLogs.value.filter(activity => activity.type === 'analysis').length
})

// Helper methods for activity display
const getActivityTypeLabel = (type) => {
  const labels = {
    'login': 'Inicio de sesión',
    'logout': 'Cierre de sesión',
    'analysis': 'Análisis de imagen'
  }
  return labels[type] || type
}

const getActivityBadgeClass = (type) => {
  const classes = {
    'login': 'bg-green-100 text-green-800',
    'logout': 'bg-orange-100 text-orange-800',
    'analysis': 'bg-blue-100 text-blue-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

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

const formatDateHeader = (dateString) => {
  try {
    const date = new Date(dateString)
    const today = new Date()
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
    
    if (date.toDateString() === today.toDateString()) return 'Hoy'
    if (date.toDateString() === yesterday.toDateString()) return 'Ayer'
    
    return date.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch (error) {
    return dateString
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

const loadActivityLogs = async (page = 1) => {
  try {
    loading.value = true
    error.value = null
    
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    const response = await fetch(`${apiUrl}/users/stats`, {
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
    
    if (data.success !== false && (data.recentSessions || data.recentAnalyses)) {
      // Combine sessions and analyses into activity logs
      const logs = []
      
      // Add session activities
      if (data.recentSessions) {
        data.recentSessions.forEach(session => {
          // Login activity
          logs.push({
            id: session.id,
            type: 'login',
            timestamp: new Date(session.loginAt),
            title: 'Inicio de sesión',
            subtitle: `IP: ${session.ipAddress || 'No disponible'}`,
            icon: '🔓',
            color: 'bg-green-500',
            details: {
              ip: session.ipAddress || 'No disponible',
              activa: session.isActive ? 'Sí' : 'No'
            }
          })
          
          // Logout activity (if session ended)
          if (session.logoutAt) {
            logs.push({
              id: session.id + '_logout',
              type: 'logout',
              timestamp: new Date(session.logoutAt),
              title: 'Cierre de sesión',
              subtitle: `IP: ${session.ipAddress || 'No disponible'}`,
              icon: '🔒',
              color: 'bg-orange-500',
              details: {
                ip: session.ipAddress || 'No disponible'
              }
            })
          }
        })
      }
      
      // Add analysis activities
      if (data.recentAnalyses) {
        data.recentAnalyses.forEach(analysis => {
          logs.push({
            id: analysis.id,
            type: 'analysis',
            timestamp: new Date(analysis.createdOn),
            title: 'Análisis de imagen completado',
            subtitle: analysis.result,
            icon: '🔬',
            color: 'bg-blue-500',
            details: {
              resultado: analysis.result,
              confianza: analysis.confidence ? `${Math.round(analysis.confidence * 100)}%` : 'N/A',
              modelo: analysis.modelId || 'Desconocido'
            }
          })
        })
      }
      
      // Sort by timestamp (newest first)
      logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      
      if (page === 1) {
        activityLogs.value = logs
      } else {
        activityLogs.value = [...activityLogs.value, ...logs]
      }
      
      // For now, no pagination - set hasMore to false
      hasMore.value = false
    } else {
      throw new Error(data.error || 'Failed to fetch activity logs')
    }
  } catch (err) {
    console.error('Error fetching activity logs:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const loadMoreLogs = async () => {
  if (loading.value || !hasMore.value) return
  
  currentPage.value += 1
  await loadActivityLogs(currentPage.value)
}

// Add and remove keyboard event listeners
onMounted(async () => {
  document.addEventListener('keydown', handleKeydown)
  await loadActivityLogs()
})

onUnmounted(() => {
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

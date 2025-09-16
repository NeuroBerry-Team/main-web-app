<template>
  <!-- Only render modal if we're on the exact activity route, not child routes -->
  <Teleport to="body" v-if="shouldShowModal">
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
                  <p class="text-2xl font-bold text-gray-900">
                    <span v-if="loading">...</span>
                    <span v-else-if="error">Error</span>
                    <span v-else>{{ analysisCount }}</span>
                  </p>
                </div>
                <div class="text-3xl text-blue-500">🔍</div>
              </div>
            </div>
            
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-green-500 hover:shadow-xl transition-shadow duration-300">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-600">Último Acceso</p>
                  <p class="text-2xl font-bold text-gray-900">
                    <span v-if="loading">...</span>
                    <span v-else-if="error">Error</span>
                    <span v-else>{{ lastAccess }}</span>
                  </p>
                </div>
                <div class="text-3xl text-green-500">⏰</div>
              </div>
            </div>
            
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-purple-500 hover:shadow-xl transition-shadow duration-300">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-600">Días Activos (mes)</p>
                  <p class="text-2xl font-bold text-gray-900">
                    <span v-if="loading">...</span>
                    <span v-else-if="error">Error</span>
                    <span v-else>{{ userStats?.summary?.activeDaysThisMonth || 0 }}</span>
                  </p>
                </div>
                <div class="text-3xl text-purple-500">📅</div>
              </div>
            </div>
          </div>

          <!-- Recent Analysis Section -->
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
            <div class="flex items-center space-x-3 mb-6">
              <div class="text-2xl">📊</div>
              <h3 class="text-xl font-bold text-gray-800">Análisis Recientes</h3>
            </div>
            
            <div v-if="loading" class="text-center py-4">
              <p class="text-gray-500">Cargando análisis...</p>
            </div>
            
            <div v-else-if="error" class="text-center py-4">
              <p class="text-red-500">Error al cargar los análisis</p>
            </div>
            
            <div v-else-if="!userStats?.recentAnalyses?.length" class="text-center py-8">
              <div class="text-4xl mb-4">📊</div>
              <p class="text-gray-500 mb-2">No hay análisis recientes</p>
              <p class="text-sm text-gray-400 mb-4">Realiza tu primer análisis de imagen</p>
              <router-link to="/AI/inference" 
                           class="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200">
                Crear análisis
                <span class="ml-2">→</span>
              </router-link>
            </div>
            
            <div v-else class="space-y-4">
              <router-link
                v-for="analysis in userStats.recentAnalyses.slice(0, 3)"
                :key="analysis.id"
                :to="`/profile/activity/inferences?id=${analysis.id}`"
                class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors duration-200 block"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <span class="text-green-600 font-semibold">🍓</span>
                  </div>
                  <div>
                    <p class="font-semibold text-gray-800">{{ analysis.result }}</p>
                    <p class="text-sm text-gray-600">
                      {{ formatActivityTime(analysis.createdOn) }}
                      <span v-if="analysis.confidence" class="ml-2">
                        • Confianza: {{ Math.round(analysis.confidence * 100) }}% 
                      </span> <!-- TODO: Get the proper confidence, this is hardcoded -->
                    </p>
                  </div>
                </div>
                <div class="text-sm text-gray-500">
                  {{ new Date(analysis.createdOn).toLocaleTimeString('es-ES', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  }) }}
                </div>
              </router-link>
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
                  <span class="font-semibold text-gray-800">
                    {{ userStats?.summary?.analysesThisWeek || 0 }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Racha de login actual</span>
                  <span class="font-semibold text-gray-800">
                    {{ userStats?.summary?.currentLoginStreak || 0 }} día{{ userStats?.summary?.currentLoginStreak !== 1 ? 's' : '' }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Funciones más utilizadas</span>
                  <span class="font-semibold text-gray-800">Análisis IA</span>
                </div>
              </div>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Días activos este mes</span>
                  <span class="font-semibold text-gray-800">
                    {{ userStats?.summary?.activeDaysThisMonth || 0 }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Total de imágenes</span>
                  <span class="font-semibold text-gray-800">
                    {{ userStats?.summary?.imagesProcessed || 0 }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-gray-600">Sesiones activas</span>
                  <span class="font-semibold text-gray-800">
                    {{ userStats?.recentSessions?.filter(s => s.isActive).length || 0 }}
                  </span>
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
            
            <div v-if="loading" class="text-center py-4">
              <p class="text-gray-500">Cargando actividad...</p>
            </div>
            
            <div v-else-if="error" class="text-center py-4">
              <p class="text-red-500">Error al cargar la actividad</p>
            </div>
            
            <div v-else-if="activityLogs.length === 0" class="text-center py-4">
              <p class="text-gray-500">No hay actividad reciente</p>
            </div>
            
            <div v-else class="space-y-3 max-h-96 overflow-y-auto">
              <div 
                v-for="activity in activityLogs" 
                :key="`${activity.type}-${activity.timestamp.getTime()}`"
                class="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                <div :class="activity.color" class="w-2 h-2 rounded-full flex-shrink-0"></div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2">
                    <span class="text-sm">{{ activity.icon }}</span>
                    <p class="text-sm font-medium text-gray-800 truncate">{{ activity.title }}</p>
                  </div>
                  <p class="text-xs text-gray-500 truncate">{{ activity.subtitle }}</p>
                </div>
                <div class="text-xs text-gray-400 flex-shrink-0">
                  {{ formatActivityTime(activity.timestamp) }}
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
  
  <!-- Render child routes when not showing the main modal -->
  <router-view v-if="!shouldShowModal" />
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted, onUnmounted, computed } from 'vue'

const router = useRouter()
const route = useRoute()
const userStats = ref(null)
const loading = ref(true)
const error = ref(null)

// Only show modal if we're on the exact activity route, not child routes
const shouldShowModal = computed(() => {
  // Show modal only for exact /profile/activity route
  return route.path === '/profile/activity'
})

const closeModal = () => {
  router.push('/profile') // Always return to the main profile page
}

// Close modal on Escape key
const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    closeModal()
  }
}

// Computed properties for easy access to stats
const analysisCount = computed(() => 
  userStats.value?.summary?.totalAnalyses || 0
)

const lastAccess = computed(() => {
  if (!userStats.value?.summary?.lastLogin) return 'Nunca'
  
  const lastLogin = new Date(userStats.value.summary.lastLogin)
  const now = new Date()
  const diffHours = Math.floor((now - lastLogin) / (1000 * 60 * 60))
  
  if (diffHours < 1) return 'Hace menos de 1 hora'
  if (diffHours < 24) return `Hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`
  
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return `Hace ${diffDays} días`
  
  return lastLogin.toLocaleDateString('es-ES')
})

// Combined activity logs (logins + analyses) sorted chronologically
const activityLogs = computed(() => {
  if (!userStats.value) return []
  
  const activities = []
  
    // Add login sessions
  if (userStats.value.recentSessions) {
    userStats.value.recentSessions.forEach(session => {
      const loginTime = new Date(session.loginAt)
      
      activities.push({
        type: 'login',
        timestamp: loginTime,
        title: session.logoutAt ? 'Sesión completada' : 'Inicio de sesión',
        // TODO: A session appears as active if the session cookie expires
        subtitle: `IP: ${session.ipAddress || 'N/A'}${session.logoutAt ? ` • Duración: ${calculateSessionDuration(session)}` : ' • Sesión activa'}`,
        color: session.logoutAt ? 'bg-green-500' : 'bg-blue-500',
        icon: '🔐'
      })
      
      // Add logout if exists
      if (session.logoutAt) {
        const logoutTime = new Date(session.logoutAt)
        
        activities.push({
          type: 'logout',
          timestamp: logoutTime,
          title: 'Cierre de sesión',
          subtitle: `IP: ${session.ipAddress || 'N/A'}`,
          color: 'bg-gray-500',
          icon: '🚪'
        })
      }
    })
  }
  
  // Add analyses
  if (userStats.value.recentAnalyses) {
    userStats.value.recentAnalyses.forEach(analysis => {
      const analysisTime = new Date(analysis.createdOn)
      
      activities.push({
        type: 'analysis',
        timestamp: analysisTime,
        title: 'Análisis completado',
        subtitle: analysis.result || 'Procesamiento de imagen exitoso',
        color: 'bg-purple-500',
        icon: '🔍'
      })
    })
  }
  
  // Sort by timestamp descending (most recent first)
  return activities
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, 15) // Limit to 15 most recent activities
})

// Helper function to calculate session duration
const calculateSessionDuration = (session) => {
  if (!session.logoutAt) return 'Activa'
  
  const login = new Date(session.loginAt)
  const logout = new Date(session.logoutAt)
  const minutes = Math.floor((logout - login) / (1000 * 60))
  
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}h ${remainingMinutes}m`
}

// Helper function to format activity timestamp
const formatActivityTime = (timestamp) => {
  try {
    if (!timestamp) return 'Sin fecha'
    
    // Convert timestamp to Date object
    const date = new Date(timestamp)
    
    // Validate date
    if (isNaN(date.getTime())) {
      console.warn('Invalid date parsed from:', timestamp)
      return 'Fecha inválida'
    }
    
    const now = new Date()
    
    // Calculate time difference
    const diffMs = now.getTime() - date.getTime()
    
    // Check for future timestamps (which shouldn't happen)
    if (diffMs < 0) {
      console.warn('Future timestamp detected:', date.toString(), 'vs now:', now.toString())
      return 'Fecha futura'
    }
    
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
    console.error('Error formatting activity time:', error, timestamp)
    return 'Error de fecha'
  }
}

// Get comprehensive user statistics from API
const getUserStats = async () => {
  try {
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
    
    if (data.success) {
      userStats.value = data
    } else {
      throw new Error(data.error || 'Failed to fetch user statistics')
    }
  } catch (err) {
    console.error('Error fetching user stats:', err)
    error.value = err.message
    userStats.value = null
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // Disable body scrolling when modal opens
  document.body.style.overflow = 'hidden'
  document.addEventListener('keydown', handleKeydown)
  
  // Fetch user statistics
  await getUserStats()
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
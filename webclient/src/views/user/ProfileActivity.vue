<template>
  <Teleport to="body" v-if="shouldShowModal">
    <transition name="modal-fade">
      <div class="modal-overlay" @click.self="closeModal">
        <div class="modal-container animated-item">
          
          <header class="modal-header">
            <div class="header-content">
              <div class="header-icon">📈</div>
              <h2 class="modal-title">Actividad del Usuario</h2>
            </div>
            <button @click="closeModal" class="close-btn" title="Cerrar ventana (ESC)">×</button>
          </header>

          <div class="modal-body">
            <section class="summary-grid animated-item" style="animation-delay: 0.1s;">
              <div class="stat-card">
                <div class="stat-content">
                  <p class="stat-label">Total Análisis</p>
                  <p class="stat-value">
                    <span v-if="loading">...</span>
                    <span v-else>{{ analysisCount }}</span>
                  </p>
                </div>
                <div class="stat-icon icon-blue">🔍</div>
              </div>
              <div class="stat-card">
                <div class="stat-content">
                  <p class="stat-label">Último Acceso</p>
                  <p class="stat-value">
                    <span v-if="loading">...</span>
                    <span v-else>{{ lastAccess }}</span>
                  </p>
                </div>
                <div class="stat-icon icon-green">⏰</div>
              </div>
              <div class="stat-card">
                <div class="stat-content">
                  <p class="stat-label">Días Activos (mes)</p>
                  <p class="stat-value">
                    <span v-if="loading">...</span>
                    <span v-else>{{ userStats?.summary?.activeDaysThisMonth || 0 }}</span>
                  </p>
                </div>
                <div class="stat-icon icon-purple">📅</div>
              </div>
            </section>

            <!-- Metrics Quick Access Card -->
            <div class="metrics-card animated-item" style="animation-delay: 0.15s;">
              <div class="metrics-content">
                <div class="metrics-icon">📊</div>
                <div class="metrics-text">
                  <h3 class="metrics-title">Métricas Detalladas</h3>
                  <p class="metrics-subtitle">Visualiza estadísticas y gráficos de tus detecciones</p>
                </div>
              </div>
              <router-link to="/profile/activity/metrics" class="metrics-btn">
                Ver Métricas →
              </router-link>
            </div>

            <div class="content-grid">
              <div class="content-section animated-item" style="animation-delay: 0.2s;">
                <h3 class="section-title">Análisis Recientes</h3>
                <div v-if="loading" class="placeholder">Cargando...</div>
                <div v-else-if="!userStats?.recentAnalyses?.length" class="placeholder">No hay análisis recientes.</div>
                <div v-else class="activity-list">
                  <router-link v-for="analysis in userStats.recentAnalyses.slice(0, 3)" :key="analysis.id" :to="`/profile/activity/inferences?id=${analysis.id}`" class="list-item">
                    <div class="item-icon icon-bg-green">🍓</div>
                    <div class="item-content">
                      <p class="item-title">{{ analysis.result }}</p>
                      <p class="item-subtitle">{{ formatActivityTime(analysis.createdOn) }}</p>
                    </div>
                    <div class="item-meta">→</div>
                  </router-link>
                </div>
                <div class="section-footer">
                  <router-link to="/profile/activity/inferences" class="footer-link">Ver todos los análisis</router-link>
                </div>
              </div>

              <div class="content-section animated-item" style="animation-delay: 0.3s;">
                <h3 class="section-title">Registro de Actividad</h3>
                 <div v-if="loading" class="placeholder">Cargando...</div>
                <div v-else-if="!activityLogs.length" class="placeholder">No hay actividad reciente.</div>
                <div v-else class="activity-list scrollable">
                  <div v-for="activity in activityLogs" :key="`${activity.type}-${activity.timestamp.getTime()}`" class="list-item">
                    <div class="item-icon" :class="activity.color">{{ activity.icon }}</div>
                    <div class="item-content">
                      <p class="item-title">{{ activity.title }}</p>
                      <p class="item-subtitle">{{ activity.subtitle }}</p>
                    </div>
                    <div class="item-meta">{{ formatActivityTime(activity.timestamp) }}</div>
                  </div>
                </div>
                 <div class="section-footer">
                  <router-link to="/profile/activity/logs" class="footer-link">Ver registro completo</router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
  
  <router-view v-if="!shouldShowModal" />
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted, onUnmounted, computed } from 'vue'

const router = useRouter()
const route = useRoute()
const userStats = ref(null)
const loading = ref(true)
const error = ref(null)

const shouldShowModal = computed(() => route.path === '/profile/activity')

const closeModal = () => router.push('/profile')

const handleKeydown = (event) => {
  if (event.key === 'Escape') closeModal()
}

const analysisCount = computed(() => userStats.value?.summary?.totalAnalyses || 0)
const lastAccess = computed(() => {
  if (!userStats.value?.summary?.lastLogin) return 'Nunca'
  const lastLogin = new Date(userStats.value.summary.lastLogin)
  const now = new Date()
  const diffHours = Math.floor((now - lastLogin) / (1000 * 60 * 60))
  if (diffHours < 1) return 'Hace menos de 1h'
  if (diffHours < 24) return `Hace ${diffHours}h`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return `Hace ${diffDays} días`
  return lastLogin.toLocaleDateString('es-ES')
})

const activityLogs = computed(() => {
  if (!userStats.value) return []
  const activities = []
  if (userStats.value.recentSessions) {
    userStats.value.recentSessions.forEach(session => {
      activities.push({
        type: 'login', timestamp: new Date(session.loginAt), title: 'Inicio de sesión',
        subtitle: `IP: ${session.ipAddress || 'N/A'}`, color: 'icon-bg-blue', icon: '🔐'
      })
    })
  }
  if (userStats.value.recentAnalyses) {
    userStats.value.recentAnalyses.forEach(analysis => {
      activities.push({
        type: 'analysis', timestamp: new Date(analysis.createdOn), title: 'Análisis completado',
        subtitle: analysis.result || 'Procesamiento exitoso', color: 'icon-bg-purple', icon: '🔍'
      })
    })
  }
  return activities.sort((a, b) => b.timestamp - a.timestamp).slice(0, 15)
})

const formatActivityTime = (timestamp) => {
  try {
    if (!timestamp) return 'Sin fecha'
    const date = new Date(timestamp)
    if (isNaN(date.getTime())) return 'Fecha inválida'
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    if (diffMs < 0) return 'Fecha futura'
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    if (diffMinutes < 1) return 'Ahora'
    if (diffMinutes < 60) return `Hace ${diffMinutes}m`
    const diffHours = Math.floor(diffMinutes / 60)
    if (diffHours < 24) return `Hace ${diffHours}h`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays === 1) return 'Ayer'
    return `Hace ${diffDays} días`
  } catch (e) {
    return 'Error'
  }
}

const getUserStats = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_BASE_URL
    const response = await fetch(`${apiUrl}/users/stats`, {
      method: 'GET', credentials: 'include', headers: { 'Content-Type': 'application/json' }
    })
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    if (data.success) {
      userStats.value = data
    } else {
      throw new Error(data.error || 'Failed to fetch user statistics')
    }
  } catch (err) {
    error.value = err.message
    userStats.value = null
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  document.body.style.overflow = 'hidden'
  document.addEventListener('keydown', handleKeydown)
  await getUserStats()
})
onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* --- Estilo del Modal --- */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(10, 20, 30, 0.6);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 1rem;
}
.modal-container {
  background-color: #f8fafc; /* Gris muy claro */
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
  max-width: 1200px; width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex; flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header {
  background: linear-gradient(45deg, #b91c1c, #7f1d1d);
  color: white;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.header-content { display: flex; align-items: center; gap: 1rem; }
.header-icon { font-size: 1.8rem; }
.modal-title { font-size: 1.5rem; font-weight: 700; }
.close-btn {
  font-size: 2rem; font-weight: 300; line-height: 1;
  background: none; border: none; color: rgba(255, 255, 255, 0.7);
  cursor: pointer; transition: all 0.2s ease;
}
.close-btn:hover { color: #fff; transform: rotate(90deg) scale(1.1); }

.modal-body {
  padding: 2rem;
  overflow-y: auto;
  display: flex; flex-direction: column; gap: 2rem;
}

/* --- Tarjetas de Resumen --- */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

/* --- Tarjeta de Métricas --- */
.metrics-card {
  background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(185, 28, 28, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-bottom: 1.5rem;
}
.metrics-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(185, 28, 28, 0.3);
}
.metrics-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}
.metrics-icon {
  font-size: 2.5rem;
  background: rgba(255, 255, 255, 0.15);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}
.metrics-text {
  color: white;
}
.metrics-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: white;
}
.metrics-subtitle {
  font-size: 0.9rem;
  margin: 0.25rem 0 0 0;
  color: rgba(255, 255, 255, 0.85);
}
.metrics-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
  white-space: nowrap;
}
.metrics-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(4px);
}
.stat-card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.07); }
.stat-label { font-size: 0.9rem; font-weight: 500; color: #6b7280; }
.stat-value { font-size: 1.75rem; font-weight: 700; color: #111827; }
.stat-icon { font-size: 2rem; }
.icon-blue { color: #3b82f6; }
.icon-green { color: #16a34a; }
.icon-purple { color: #9333ea; }

/* --- Secciones de Contenido --- */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}
.content-section {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
}
.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #b91c1c;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
}
.placeholder { text-align: center; padding: 1rem; color: #6b7280; }

/* --- Listas de Actividad --- */
.activity-list { display: flex; flex-direction: column; gap: 1rem; }
.scrollable { max-height: 300px; overflow-y: auto; padding-right: 0.5rem; }
.list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  transition: background-color 0.2s ease;
  text-decoration: none;
}
.list-item:hover { background-color: #f9fafb; }
.item-icon {
  width: 2.5rem; height: 2.5rem;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}
.icon-bg-blue { background-color: #dbeafe; color: #1d4ed8; }
.icon-bg-green { background-color: #dcfce7; color: #166534; }
.icon-bg-purple { background-color: #f3e8ff; color: #6b21a8; }
.item-content { flex: 1; min-width: 0; }
.item-title { font-weight: 600; color: #374151; }
.item-subtitle { font-size: 0.8rem; color: #6b7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-meta { font-size: 0.8rem; color: #9ca3af; }

.section-footer { margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; }
.footer-link {
  color: #b91c1c;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s ease;
}
.footer-link:hover { color: #991b1b; }

/* --- Animaciones --- */
.animated-item {
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.modal-fade-enter-active, .modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from, .modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-active .modal-container {
  transition: transform 0.3s ease;
}
.modal-fade-leave-active .modal-container {
  transition: transform 0.3s ease;
}
.modal-fade-enter-from .modal-container {
  transform: scale(0.95);
}
.modal-fade-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
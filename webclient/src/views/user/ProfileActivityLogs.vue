<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div class="modal-overlay" @click.self="goBack">
        <div class="modal-container animated-item">

          <header class="modal-header">
            <div class="header-content">
              <div class="header-icon">📋</div>
              <h2 class="modal-title">Registro de Actividad</h2>
            </div>
            <button @click="goBack" class="close-btn" title="Cerrar (ESC)">×</button>
          </header>

          <div class="modal-body">
            <div v-if="loading" class="placeholder-content"><div class="spinner-large"></div><p>Cargando registro...</p></div>
            <div v-else-if="error" class="placeholder-content"><div class="placeholder-icon">❌</div><h3 class="placeholder-title">Error al Cargar</h3><p>{{ error }}</p></div>
            <div v-else-if="!activityLogs.length" class="placeholder-content">
              <div class="placeholder-icon">📋</div>
              <h3 class="placeholder-title">No hay actividad registrada</h3>
              <p class="placeholder-text">Tus acciones en la plataforma aparecerán aquí.</p>
            </div>
            
            <div v-else class="timeline-wrapper">
              <section class="summary-grid">
                <div class="stat-card">
                  <div class="stat-content">
                    <p class="stat-label">Inicios de sesión</p>
                    <p class="stat-value">{{ loginCount }}</p>
                  </div>
                  <div class="stat-icon icon-green">🔓</div>
                </div>
                <div class="stat-card">
                  <div class="stat-content">
                    <p class="stat-label">Análisis realizados</p>
                    <p class="stat-value">{{ analysisCount }}</p>
                  </div>
                  <div class="stat-icon icon-blue">🔬</div>
                </div>
                <div class="stat-card">
                  <div class="stat-content">
                    <p class="stat-label">Total actividades</p>
                    <p class="stat-value">{{ activityLogs.length }}</p>
                  </div>
                  <div class="stat-icon icon-orange">📊</div>
                </div>
              </section>

              <section class="timeline">
                <div v-for="(activities, dateKey) in groupedActivities" :key="dateKey" class="timeline-group">
                  <h3 class="timeline-date-header">{{ formatDateHeader(dateKey) }}</h3>
                  <div class="activity-items">
                    <div v-for="activity in activities" :key="activity.id" class="activity-card">
                      <div class="activity-icon" :class="activity.color">{{ activity.icon }}</div>
                      <div class="activity-content">
                        <div class="content-header">
                          <h4>{{ activity.title }}</h4>
                          <span class="timestamp">{{ formatTime(activity.timestamp) }}</span>
                        </div>
                        <p class="subtitle">{{ activity.subtitle }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <div v-if="hasMore && !loading" class="load-more-container">
                <button @click="loadMoreLogs" class="action-btn btn-secondary">Cargar más</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const activityLogs = ref([]);
const loading = ref(true);
const error = ref(null);
const hasMore = ref(false);
const currentPage = ref(1);

const goBack = () => router.push('/profile/activity');
const handleKeydown = (event) => { if (event.key === 'Escape') goBack(); };

const groupedActivities = computed(() => {
  if (!activityLogs.value.length) return {};
  const groups = {};
  activityLogs.value.forEach(activity => {
    const dateKey = activity.timestamp.toDateString();
    if (!groups[dateKey]) groups[dateKey] = [];
    groups[dateKey].push(activity);
  });
  Object.keys(groups).forEach(date => {
    groups[date].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  });
  return groups;
});

const loginCount = computed(() => activityLogs.value.filter(a => a.type === 'login').length);
const analysisCount = computed(() => activityLogs.value.filter(a => a.type === 'analysis').length);

const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
const formatDateHeader = (dateString) => {
  const date = new Date(dateString);
  const today = new Date();
  const yesterday = new Date(today.getTime() - 86400000);
  if (date.toDateString() === today.toDateString()) return 'Hoy';
  if (date.toDateString() === yesterday.toDateString()) return 'Ayer';
  return date.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
};

const loadActivityLogs = async (page = 1) => {
  try {
    loading.value = true;
    error.value = null;
    const apiUrl = import.meta.env.VITE_API_BASE_URL;
    const response = await fetch(`${apiUrl}/users/stats`, {
      method: 'GET', credentials: 'include', headers: { 'Content-Type': 'application/json' }
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    if (data.success !== false && (data.recentSessions || data.recentAnalyses)) {
      const logs = [];
      if (data.recentSessions) {
        data.recentSessions.forEach(session => {
          logs.push({
            id: session.id, type: 'login', timestamp: new Date(session.loginAt),
            title: 'Inicio de sesión', subtitle: `IP: ${session.ipAddress || 'N/A'}`,
            icon: '🔓', color: 'icon-bg-green'
          });
          if (session.logoutAt) {
            logs.push({
              id: `${session.id}_logout`, type: 'logout', timestamp: new Date(session.logoutAt),
              title: 'Cierre de sesión', subtitle: `IP: ${session.ipAddress || 'N/A'}`,
              icon: '🔒', color: 'icon-bg-orange'
            });
          }
        });
      }
      if (data.recentAnalyses) {
        data.recentAnalyses.forEach(analysis => {
          logs.push({
            id: analysis.id, type: 'analysis', timestamp: new Date(analysis.createdOn),
            title: 'Análisis de imagen', subtitle: analysis.result,
            icon: '🔬', color: 'icon-bg-blue'
          });
        });
      }
      logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      activityLogs.value = page === 1 ? logs : [...activityLogs.value, ...logs];
      hasMore.value = false;
    } else {
      throw new Error(data.error || 'Failed to fetch logs');
    }
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
const loadMoreLogs = async () => {
  if (loading.value || !hasMore.value) return;
  currentPage.value++;
  await loadActivityLogs(currentPage.value);
};

onMounted(async () => {
  document.addEventListener('keydown', handleKeydown);
  await loadActivityLogs();
});
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
/* --- Estilos Generales del Modal --- */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(10, 20, 30, 0.6);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 1rem;
}
.modal-container {
  background-color: #f8fafc;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
  max-width: 1000px; width: 100%;
  height: 90vh;
  overflow: hidden;
  display: flex; flex-direction: column;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.modal-header {
  background: linear-gradient(45deg, #b91c1c, #7f1d1d);
  color: white; padding: 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
  text-shadow: 0 1px 3px rgba(0,0,0,0.2);
  flex-shrink: 0;
}
.header-content { display: flex; align-items: center; gap: 1rem; }
.header-icon { font-size: 1.8rem; }
.modal-title { font-size: 1.5rem; font-weight: 700; }
.close-btn {
  font-size: 2rem; font-weight: 300; line-height: 1;
  background: none; border: none; color: rgba(255,255,255,0.7);
  cursor: pointer; transition: all 0.2s ease;
}
.close-btn:hover { color: #fff; transform: rotate(90deg) scale(1.1); }
.modal-body { padding: 2rem; overflow-y: auto; }

/* --- Placeholder y Carga --- */
.placeholder-content { text-align: center; padding: 4rem 1rem; color: #6b7280; }
.placeholder-icon { font-size: 3rem; margin-bottom: 1rem; }
.placeholder-title { font-size: 1.25rem; font-weight: 700; color: #374151; }
.spinner-large { width: 2.5rem; height: 2.5rem; border: 4px solid #d1d5db; border-top-color: #b91c1c; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem auto; }

/* --- Línea de Tiempo --- */
.timeline-wrapper { display: flex; flex-direction: column; gap: 2rem; }
.summary-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}
.stat-card {
  background-color: #fff; padding: 1.5rem; border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05); border: 1px solid #e5e7eb;
  display: flex; align-items: center; gap: 1rem;
}
.stat-label { font-size: 0.9rem; font-weight: 500; color: #6b7280; }
.stat-value { font-size: 1.75rem; font-weight: 700; color: #111827; }
.stat-icon { font-size: 1.8rem; padding: 0.75rem; border-radius: 8px; }
.icon-green { color: #166534; background-color: #dcfce7; }
.icon-blue { color: #1d4ed8; background-color: #dbeafe; }
.icon-orange { color: #9a3412; background-color: #ffedd5; }

.timeline-group { display: flex; flex-direction: column; gap: 1rem; }
.timeline-date-header {
  font-weight: 600; font-size: 1.1rem; color: #b91c1c;
  padding-bottom: 0.5rem; border-bottom: 2px solid #fde2e2;
}
.activity-items { display: flex; flex-direction: column; gap: 1rem; }
.activity-card {
  background-color: #fff; border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.04); border: 1px solid #e5e7eb;
  padding: 1rem; display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.activity-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
.activity-icon {
  width: 2.5rem; height: 2.5rem; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; color: white;
}
.icon-bg-green { background-color: #16a34a; }
.icon-bg-orange { background-color: #f97316; }
.icon-bg-blue { background-color: #2563eb; }
.activity-content { flex: 1; min-width: 0; }
.content-header { display: flex; justify-content: space-between; align-items: baseline; }
.activity-content h4 { font-weight: 600; color: #374151; }
.activity-content .subtitle { font-size: 0.9rem; color: #6b7280; }
.timestamp { font-size: 0.8rem; color: #9ca3af; }

.load-more-container { text-align: center; margin-top: 1rem; }

/* --- Botones --- */
.action-btn {
  display: inline-flex; align-items: center; justify-content: center;
  gap: 0.5rem; padding: 0.7rem 1.5rem; border-radius: 8px;
  font-weight: 600; border: none; cursor: pointer; transition: all 0.2s ease;
}
.action-btn:hover { transform: translateY(-2px); }
.btn-primary { background-color: #b91c1c; color: white; }
.btn-secondary { background-color: #e5e7eb; color: #374151; }

/* --- Animaciones --- */
.animated-item { opacity: 0; animation: fadeInUp 0.5s ease-out forwards; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
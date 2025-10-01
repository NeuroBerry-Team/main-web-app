<template>
  <div class="training-manager-wrapper">
    <section class="hero-section animated-item">
      <h1 class="hero-title">🔄 Gestión de Entrenamientos</h1>
      <p class="hero-text">
        {{ isSuperAdmin ? 'Gestiona todos los trabajos de entrenamiento del sistema.' : 'Gestiona tus trabajos de entrenamiento activos.' }}
      </p>
      <div class="user-info">
        <span class="role-badge role-admin">{{ user?.role }}</span>
        <span v-if="isSuperAdmin" class="superadmin-tag">(Acceso completo)</span>
      </div>
    </section>

    <section class="content-section animated-item" style="animation-delay: 0.1s;">
      <div class="filters-container">
        <div class="filter-tabs">
          <button 
            v-for="status in statusFilters" 
            :key="status.value"
            @click="activeFilter = status.value"
            class="filter-tab"
            :class="{ 'active': activeFilter === status.value }"
          >
            {{ status.label }}
            <span v-if="getJobCountByStatus(status.value) > 0" class="tab-counter">
              {{ getJobCountByStatus(status.value) }}
            </span>
          </button>
        </div>
        <button @click="refreshJobs" :disabled="isLoading" class="action-btn btn-primary">
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>🔄</span>
          {{ isLoading ? 'Actualizando...' : 'Actualizar' }}
        </button>
      </div>
    </section>

    <section class="content-section animated-item" style="animation-delay: 0.2s;">
      <div v-if="isLoading && trainingJobs.length === 0" class="placeholder-content">
        <div class="spinner-large"></div>
        <p>Cargando trabajos de entrenamiento...</p>
      </div>
      <div v-else-if="filteredJobs.length === 0" class="placeholder-content">
        <div class="placeholder-icon">📝</div>
        <h3 class="placeholder-title">No hay entrenamientos</h3>
        <p class="placeholder-text">
          {{ activeFilter === 'all' ? 'No se encontraron trabajos.' : `No hay trabajos con estado "${getStatusLabel(activeFilter)}".` }}
        </p>
      </div>
      <div v-else class="jobs-list">
        <div v-for="(job, index) in filteredJobs" :key="job.jobId" class="job-card animated-item" :style="{'animation-delay': `${0.3 + index * 0.05}s`}">
          <div class="job-header">
            <div class="job-title-group">
              <h3>{{ job.trainingData?.modelName || 'Modelo sin nombre' }}</h3>
              <span class="status-badge" :class="getStatusBadgeClass(job.status)">{{ getStatusLabel(job.status) }}</span>
            </div>
            <div class="job-actions">
              <button @click="viewJobDetails(job)" class="job-action-btn">👁️ Detalles</button>
              <button v-if="canCancelJob(job)" @click="confirmCancelJob(job)" :disabled="isCancelling[job.jobId]" class="job-action-btn btn-cancel">
                <span v-if="isCancelling[job.jobId]" class="spinner-small"></span>
                {{ isCancelling[job.jobId] ? 'Cancelando...' : '❌ Cancelar' }}
              </button>
            </div>
          </div>
          <div v-if="job.status === 'running' && job.progress" class="progress-section">
            <div class="progress-info">
              <span>Progreso: {{ job.progress.stage || 'En proceso' }}</span>
              <span>{{ job.progress.percentage || 0 }}%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" :style="`width: ${job.progress.percentage || 0}%`"></div>
            </div>
          </div>
          <div class="job-details">
            <p><strong>ID:</strong> {{ job.jobId }}</p>
            <p><strong>Tipo:</strong> {{ job.trainingData?.modelType || 'N/A' }}</p>
            <p><strong>Creado:</strong> {{ formatDate(job.createdAt) }}</p>
            <p v-if="job.trainingData?.trainingParams"><strong>Épocas:</strong> {{ job.trainingData.trainingParams.epochs }}</p>
          </div>
          <div v-if="job.status === 'failed' && job.errorMessage" class="error-message">
            <h4>❌ Error</h4>
            <p>{{ job.errorMessage }}</p>
          </div>
        </div>
      </div>
    </section>

    <transition name="fade">
      <div v-if="showCancelModal" class="modal-overlay" @click="showCancelModal = false">
        <div class="modal-content" @click.stop>
          <h3 class="modal-title">⚠️ Confirmar Cancelación</h3>
          <p class="modal-text">
            ¿Estás seguro de que deseas cancelar el entrenamiento <strong>{{ jobToCancel?.trainingData?.modelName }}</strong>? Esta acción no se puede deshacer.
          </p>
          <div class="modal-actions">
            <button @click="showCancelModal = false" class="action-btn btn-secondary">No, volver</button>
            <button @click="cancelJob" :disabled="isCancelling[jobToCancel?.jobId]" class="action-btn btn-danger">
              {{ isCancelling[jobToCancel?.jobId] ? 'Cancelando...' : 'Sí, Cancelar' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAuth } from '../../composables/use_auth.js';
import { useCSRF } from '../../composables/use_csrf.js';

const { isSuperAdmin, user, checkAuthStatus, isLoggedIn, isAdmin } = useAuth();
const { makeSecureRequest } = useCSRF();
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
const trainingJobs = ref([]);
const isLoading = ref(false);
const error = ref('');
const activeFilter = ref('all');
const showCancelModal = ref(false);
const jobToCancel = ref(null);
const isCancelling = ref({});
const refreshInterval = ref(null);
const statusFilters = ref([
  { value: 'all', label: 'Todos' },
  { value: 'pending', label: 'Pendiente' },
  { value: 'running', label: 'Ejecutando' },
  { value: 'completed', label: 'Completado' },
  { value: 'failed', label: 'Fallido' },
  { value: 'cancelled', label: 'Cancelado' }
]);

const filteredJobs = computed(() => {
  if (activeFilter.value === 'all') return trainingJobs.value;
  return trainingJobs.value.filter(job => job.status === activeFilter.value);
});
const fetchTrainingJobs = async () => {
  try {
    isLoading.value = true;
    error.value = '';
    const response = await makeSecureRequest(`${apiUrl}/models/training-jobs`, { method: 'GET' });
    if (response.ok) {
      const data = await response.json();
      trainingJobs.value = data.jobs || [];
    } else {
      const errorData = await response.json().catch(() => ({}));
      error.value = errorData.message || `Error ${response.status}: ${response.statusText}`;
    }
  } catch (err) {
    error.value = 'Error al cargar los trabajos de entrenamiento';
  } finally {
    isLoading.value = false;
  }
};
const refreshJobs = async () => await fetchTrainingJobs();
const canCancelJob = (job) => {
  if (!['pending', 'running'].includes(job.status)) return false;
  if (isSuperAdmin.value) return true;
  return true;
};
const confirmCancelJob = (job) => {
  jobToCancel.value = job;
  showCancelModal.value = true;
};
const cancelJob = async () => {
  if (!jobToCancel.value) return;
  const jobId = jobToCancel.value.jobId;
  isCancelling.value[jobId] = true;
  try {
    const response = await makeSecureRequest(`${apiUrl}/models/training-jobs/${jobId}`, { method: 'DELETE' });
    if (response.ok) {
      showCancelModal.value = false;
      jobToCancel.value = null;
      await refreshJobs();
    } else {
      const errorData = await response.json().catch(() => ({}));
      error.value = errorData.message || 'Error al cancelar el entrenamiento';
    }
  } catch (err) {
    error.value = 'Error al cancelar el entrenamiento';
  } finally {
    isCancelling.value[jobId] = false;
  }
};
const viewJobDetails = (job) => console.log('View job details:', job);
const getJobCountByStatus = (status) => {
  if (status === 'all') return trainingJobs.value.length;
  return trainingJobs.value.filter(job => job.status === status).length;
};
const getStatusLabel = (status) => statusFilters.value.find(f => f.value === status)?.label || status;
const getStatusBadgeClass = (status) => `status-${status}`;
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString('es-ES', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
};
const startAutoRefresh = () => {
  refreshInterval.value = setInterval(async () => {
    const hasActiveJobs = trainingJobs.value.some(job => ['pending', 'running'].includes(job.status));
    if (hasActiveJobs && !isLoading.value) {
      await fetchTrainingJobs();
    }
  }, 3000);
};
const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value);
    refreshInterval.value = null;
  }
};
onMounted(async () => {
  await checkAuthStatus();
  if (isLoggedIn.value && isAdmin.value) {
    await fetchTrainingJobs();
    startAutoRefresh();
  }
});
onUnmounted(() => stopAutoRefresh());
</script>

<style scoped>
/* --- ESTILOS VISUALES COHERENTES --- */
.training-manager-wrapper { display: flex; flex-direction: column; gap: 2rem; }
.content-section {
  background-color: #fff; border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07); padding: 2rem;
}
.hero-section {
  background: linear-gradient(45deg, #b91c1c, #7f1d1d); color: white;
  padding: 2.5rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(185, 28, 28, 0.25);
}
.hero-title { font-size: 1.8rem; font-weight: 800; }
.hero-text { color: rgba(255, 255, 255, 0.9); margin-top: 0.25rem; }
.user-info { display: flex; align-items: center; gap: 0.75rem; margin-top: 1rem; }
.role-badge { background-color: rgba(255, 255, 255, 0.2); color: #fff; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; }
.superadmin-tag { color: #f59e0b; font-weight: 600; }

/* --- Filtros --- */
.filters-container { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
.filter-tabs { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.filter-tab {
  padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem;
  background-color: #f3f4f6; color: #4b5563; border: none; cursor: pointer;
  transition: all 0.2s ease; display: flex; align-items: center; gap: 0.5rem;
}
.filter-tab:hover { background-color: #e5e7eb; }
.filter-tab.active { background-color: #b91c1c; color: white; box-shadow: 0 4px 15px rgba(185, 28, 28, 0.2); }
.tab-counter { background-color: rgba(255,255,255,0.2); padding: 0.1rem 0.5rem; border-radius: 10px; font-size: 0.75rem; }
.filter-tab:not(.active) .tab-counter { background-color: #e5e7eb; color: #4b5563; }

/* --- Lista de Trabajos --- */
.placeholder-content { text-align: center; padding: 2rem; color: #6b7280; }
.placeholder-icon { font-size: 3rem; margin-bottom: 1rem; }
.placeholder-title { font-size: 1.25rem; font-weight: 700; color: #374151; }
.jobs-list { display: flex; flex-direction: column; gap: 1.5rem; }
.job-card {
  border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem;
  transition: box-shadow 0.2s ease;
}
.job-card:hover { box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
.job-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;}
.job-title-group { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.job-title-group h3 { font-size: 1.25rem; font-weight: 700; color: #1f2937; }
.job-actions { display: flex; gap: 0.5rem; }
.job-action-btn {
  padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem;
  background-color: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; cursor: pointer;
  transition: all 0.2s ease;
}
.job-action-btn:hover { background-color: #e5e7eb; }
.job-action-btn.btn-cancel { background-color: #fee2e2; color: #b91c1c; border-color: #fecaca; }
.job-action-btn.btn-cancel:hover { background-color: #fecaca; }
.progress-section { margin-bottom: 1rem; }
.progress-info { display: flex; justify-content: space-between; font-size: 0.9rem; font-weight: 500; margin-bottom: 0.5rem; }
.progress-bar-container { width: 100%; background-color: #e5e7eb; border-radius: 9999px; height: 0.5rem; }
.progress-bar-fill { background-color: #b91c1c; height: 100%; border-radius: 9999px; transition: width 0.3s ease; }
.job-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem; font-size: 0.9rem; color: #4b5563; }
.error-message { background-color: #fee2e2; border: 1px solid #fecaca; color: #991b1b; padding: 1rem; border-radius: 8px; margin-top: 1rem; }
.error-message h4 { font-weight: 700; }

/* --- Insignias de Estado --- */
.status-badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; }
.status-pending { background-color: #fef3c7; color: #92400e; }
.status-running { background-color: #dcfce7; color: #166534; }
.status-completed { background-color: #d1fae5; color: #065f46; }
.status-failed { background-color: #fee2e2; color: #991b1b; }
.status-cancelled { background-color: #f3f4f6; color: #374151; }

/* --- Modal --- */
.modal-overlay { position: fixed; inset: 0; background-color: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-content {
  background-color: white; border-radius: 15px; padding: 2rem;
  max-width: 500px; width: 90%; box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}
.modal-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; }
.modal-text { color: #4b5563; margin-bottom: 1.5rem; }
.modal-actions { display: flex; justify-content: flex-end; gap: 0.75rem; }
.action-btn { padding: 0.6rem 1.5rem; border-radius: 8px; font-weight: 600; border: none; cursor: pointer; transition: all 0.2s ease; }
.btn-primary { background-color: #b91c1c; color: white; }
.btn-primary:hover { background-color: #991b1b; }
.btn-secondary { background-color: #e5e7eb; color: #374151; }
.btn-secondary:hover { background-color: #d1d5db; }
.btn-danger { background-color: #dc2626; color: white; }
.btn-danger:hover { background-color: #b91c1c; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* --- Animaciones --- */
.animated-item { opacity: 0; animation: fadeInUp 0.7s ease-out forwards; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease-in-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.spinner, .spinner-large, .spinner-small { border-radius: 50%; animation: spin 1s linear infinite; }
.spinner { width: 1.25rem; height: 1.25rem; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; }
.spinner-large { width: 2rem; height: 2rem; border: 4px solid #d1d5db; border-top-color: #b91c1c; }
.spinner-small { width: 1rem; height: 1rem; border: 2px solid #b91c1c; border-top-color: transparent; display: inline-block; margin-right: 0.5rem; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
<template>
  <div class="page-wrapper">
    
    <div v-if="isLoggedIn && isAdmin && !authLoading" class="main-content">
      
      <section class="content-section animated-item">
        <h1 class="section-title">🏋️ Entrenamiento de Modelos IA</h1>
        <p class="section-text">
          Configura y entrena modelos de inteligencia artificial usando YOLOv8 con tus datasets personalizados.
        </p>
        <div class="user-status status-admin">
          <strong>Conectado como:</strong> {{ user?.role }}
        </div>
      </section>

      <section class="content-section animated-item" style="animation-delay: 0.1s;">
        <h2 class="form-title">Configuración de Entrenamiento</h2>
        
        <form @submit.prevent="handleTraining" class="training-form">
          <div class="form-group">
            <label class="form-label">Dataset <span class="required">*</span></label>
            <select v-model.number="trainingConfig.datasetId" required :disabled="isTraining" class="form-input">
              <option :value="null">Selecciona un dataset</option>
              <option v-for="dataset in availableDatasets" :key="dataset.id" :value="dataset.id">
                {{ dataset.name }} - {{ dataset.description || 'Sin descripción' }}
              </option>
            </select>
            <p class="form-description">Selecciona el dataset que se utilizará para entrenar el modelo.</p>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Tipo de Modelo</label>
              <select v-model="trainingConfig.modelType" :disabled="isTraining" class="form-input">
                <option value="YOLOv8_m">YOLOv8 Medium (Recomendado)</option>
              </select>
              <p class="form-description">Por ahora solo disponible YOLOv8 Medium.</p>
            </div>
            <div class="form-group">
              <label class="form-label">Nombre del Modelo <span class="required">*</span></label>
              <input v-model="trainingConfig.modelName" type="text" required :disabled="isTraining" placeholder="Ej: FrambuesiasModel_v1" class="form-input" />
              <p class="form-description">Nombre único para identificar tu modelo.</p>
            </div>
          </div>

          <div class="form-subsection">
            <h3 class="subsection-title">Parámetros de Entrenamiento</h3>
            <div class="form-grid-3">
              <div class="form-group">
                <label class="form-label">Épocas</label>
                <input v-model.number="trainingConfig.epochs" type="number" min="1" max="1000" :disabled="isTraining" class="form-input" />
                <p class="form-description"><strong>Recomendado:</strong> 20-100</p>
              </div>
              <div class="form-group">
                <label class="form-label">Tamaño de Imagen</label>
                <select v-model.number="trainingConfig.imageSize" :disabled="isTraining" class="form-input">
                  <option :value="640">640x640 (Recomendado)</option>
                  <option :value="416">416x416</option>
                  <option :value="512">512x512</option>
                  <option :value="800">800x800</option>
                </select>
                 <p class="form-description">Precisión vs. velocidad.</p>
              </div>
              <div class="form-group">
                <label class="form-label">Tamaño de Lote</label>
                <select v-model.number="trainingConfig.batchSize" :disabled="isTraining" class="form-input">
                  <option :value="16">16 (Recomendado)</option>
                  <option :value="8">8</option>
                  <option :value="32">32</option>
                  <option :value="64">64</option>
                </select>
                <p class="form-description">Ajustar según VRAM.</p>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Descripción del Modelo</label>
            <textarea v-model="trainingConfig.description" rows="3" :disabled="isTraining" placeholder="Describe brevemente este modelo y su propósito..." class="form-textarea"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="resetForm" :disabled="isTraining" class="action-btn btn-secondary">
              Limpiar
            </button>
            <button type="submit" :disabled="isTraining || !isFormValid" class="action-btn btn-primary">
              <span v-if="isTraining" class="spinner"></span>
              <span>{{ isTraining ? 'Iniciando...' : 'Iniciar Entrenamiento' }}</span>
            </button>
          </div>
        </form>
      </section>

      <section v-if="error" class="alert alert-error animated-item" style="animation-delay: 0.2s;">
        <h4>Error</h4>
        <p>{{ error }}</p>
      </section>
      <section v-if="successMessage" class="alert alert-success animated-item" style="animation-delay: 0.2s;">
        <h4>¡Éxito!</h4>
        <p>{{ successMessage }}</p>
      </section>

      <section class="alert alert-info animated-item" style="animation-delay: 0.3s;">
        <h4>ℹ️ Información Importante</h4>
        <p>El entrenamiento es un proceso asíncrono que se ejecuta en segundo plano. Puede tomar desde minutos hasta horas, dependiendo de la configuración. Recibirás una notificación cuando finalice.</p>
      </section>

    </div>

    <div v-else>
      <section v-if="authLoading" class="loading-section">
        <h1 class="loading-text">Verificando autenticación...</h1>
      </section>
      <section v-if="!authLoading" class="content-section animated-item">
        <div class="access-denied-icon">🔒</div>
        <h1 class="section-title">Acceso Restringido</h1>
        <p class="section-text">Esta sección está disponible solo para administradores.</p>
        <router-link v-if="!isLoggedIn" to="/login" class="action-btn btn-primary">
          Iniciar Sesión
        </router-link>
      </section>
    </div>
    
  </div>
</template>

<script setup>
// --- LÓGICA DEL COMPONENTE (SIN CAMBIOS) ---
import { ref, computed, onMounted } from 'vue';
import { useAuth } from '../../composables/use_auth.js';
import { useCSRF } from '../../composables/use_csrf.js';
import { useAudit } from '../../composables/log_audit.js';

const { isLoggedIn, isAdmin, user, loading: authLoading, checkAuthStatus } = useAuth();
const { makeSecureRequest } = useCSRF();
const { logModelTraining } = useAudit();
const apiUrl = import.meta.env.VITE_API_BASE_URL;

const availableDatasets = ref([]);
const isTraining = ref(false);
const error = ref('');
const successMessage = ref('');
const loadingDatasets = ref(false);

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
});

const isFormValid = computed(() => {
  const { datasetId, modelName, epochs, batchSize, learningRate } = trainingConfig.value;
  return (
    datasetId !== null &&
    Number.isInteger(datasetId) &&
    datasetId > 0 &&
    modelName.trim().length > 0 &&
    epochs > 0 &&
    batchSize > 0 &&
    learningRate > 0
  );
});

const fetchAvailableDatasets = async () => {
  loadingDatasets.value = true;
  error.value = '';
  try {
    const response = await makeSecureRequest(`${apiUrl}/datasets/`, { method: 'GET' });
    if (response.ok) {
      const data = await response.json();
      availableDatasets.value = data.datasets || [];
    } else {
      error.value = 'No se pudieron cargar los datasets.';
    }
  } catch (err) {
    error.value = 'Error de red al cargar los datasets.';
  } finally {
    loadingDatasets.value = false;
  }
};

const handleTraining = async () => {
  if (!isFormValid.value || isTraining.value) return;
  isTraining.value = true;
  error.value = '';
  successMessage.value = '';
  try {
    const trainingPayload = {
      datasetId: trainingConfig.value.datasetId,
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
    };
    const response = await makeSecureRequest(`${apiUrl}/models/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(trainingPayload)
    });
    const data = await response.json();
    if (response.ok) {
      successMessage.value = `¡Entrenamiento iniciado correctamente! ID del trabajo: ${data.jobId || 'N/A'}`;
      await logModelTraining(trainingPayload.modelName, trainingPayload.datasetId, trainingPayload.modelType, data.modelId);
      setTimeout(() => {
        resetForm();
        successMessage.value = '';
      }, 5000);
    } else {
      error.value = data.message || `Error ${response.status}`;
    }
  } catch (err) {
    error.value = 'Error al iniciar el entrenamiento. Por favor, inténtalo de nuevo.';
  } finally {
    isTraining.value = false;
  }
};

const resetForm = () => {
  trainingConfig.value = {
    datasetId: null, modelName: '', modelType: 'YOLOv8_m', description: '',
    epochs: 50, imageSize: 640, batchSize: 16, learningRate: 0.01, patience: 30
  };
  error.value = '';
  successMessage.value = '';
};

onMounted(async () => {
  await checkAuthStatus();
  if (isLoggedIn.value && isAdmin.value) {
    await fetchAvailableDatasets();
  }
});
</script>

<style scoped>
/* --- Estilos Generales --- */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  display: flex;
  flex-direction: column;
  gap: 3rem;
  background-color: #fff;
}
.main-content {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}
.content-section {
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07);
  padding: 2.5rem;
  text-align: center;
}
.section-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #b22222;
  margin-bottom: 0.5rem;
}
.section-text {
  max-width: 800px;
  margin: 0 auto;
  font-size: 1.1rem;
  line-height: 1.7;
  color: #555;
  margin-top: 1rem;
}

/* --- Formulario --- */
.form-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 2rem;
  text-align: left;
}
.training-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  text-align: left;
}
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
.form-grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-label { font-weight: 600; font-size: 0.9rem; color: #444; }
.required { color: #b22222; }
.form-input, .form-textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-size: 1rem;
}
.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #b22222;
  box-shadow: 0 0 0 3px rgba(178, 34, 34, 0.1);
}
.form-input:disabled { background-color: #f5f5f5; cursor: not-allowed; }
.form-description { font-size: 0.85rem; color: #777; }
.form-subsection {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.subsection-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

/* --- Botones --- */
.action-btn {
  display: flex; align-items: center; justify-content: center; gap: 0.75rem;
  padding: 0.8rem 1.8rem; border-radius: 25px; color: white;
  border: none; font-size: 1rem; font-weight: 600; cursor: pointer;
  transition: all 0.3s ease; text-decoration: none;
}
.action-btn:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
.action-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
.btn-primary { background: linear-gradient(45deg, #b22222, #e13c3c); }
.btn-secondary { background-color: #fff; color: #555; border: 1px solid #ccc; }
.btn-secondary:hover { background-color: #f5f5f5; border-color: #aaa; }

/* --- Alertas y Estados --- */
.user-status {
  margin-top: 1rem; padding: 0.5rem 1.25rem; border-radius: 20px; font-weight: 500;
  border: 1px solid transparent; display: inline-block;
}
.status-admin { background-color: #f0e6f7; color: #6b21a8; border-color: #e9d5ff; }
.loading-section { padding: 4rem; }
.loading-text { font-size: 1.5rem; font-weight: 600; color: #888; animation: pulsate 1.5s ease-in-out infinite; }
.access-denied-icon { font-size: 3rem; margin-bottom: 1rem; }
.alert {
  padding: 1.5rem; border-radius: 10px; text-align: left;
  border-left: 5px solid;
}
.alert h4 { font-weight: 700; font-size: 1.1rem; margin-bottom: 0.25rem; }
.alert-error { background-color: #fef2f2; border-color: #ef4444; color: #b91c1c; }
.alert-success { background-color: #f0fdf4; border-color: #22c55e; color: #15803d; }
.alert-info { background-color: #eff6ff; border-color: #3b82f6; color: #1e40af; }

/* --- Spinner --- */
.spinner {
  width: 1.25rem; height: 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* --- Animaciones --- */
.animated-item { opacity: 0; animation: fadeInUp 0.7s ease-out forwards; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulsate { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
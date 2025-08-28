<template>
  <div class="page-wrapper">

    <div class="logo-wrapper">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <!-- Authentication check -->
    <section v-if="!isLoggedIn && !authLoading" class="auth-required">
      <h1 class="section-title">Acceso Requerido</h1>
      <p class="big-paragraph">
        Debes iniciar sesión para acceder a la herramienta de análisis de imágenes.
      </p>
      <router-link to="/login" class="btn login-btn">Iniciar Sesión</router-link>
    </section>

    <!-- Loading authentication -->
    <section v-if="authLoading" class="loading-section">
      <h1 class="section-title">Verificando autenticación...</h1>
    </section>

    <!-- Main content - only show if authenticated -->
    <div v-if="isLoggedIn">
      <section class="hero-section">
        <h1 class="section-title">Análisis de Imágenes</h1>
        <p class="big-paragraph">
          Carga una imagen de frambuesa para iniciar el proceso de análisis con nuestra IA.
        </p>
        <p v-if="user?.role" class="user-info">
          Conectado como: <strong>{{ user.role }}</strong>
        </p>
      </section>

      <section class="upload-section">
        <div class="upload-box" @click="triggerFileInput" :class="{ disabled: loading }">
          <input
            type="file"
            ref="fileInput"
            accept="image/*"
            @change="onFileChange"
            style="display: none"
          />
          <div v-if="!previewImage" class="placeholder">
            <i class="upload-icon">📁</i>
            <span>Haz clic aquí o arrastra una imagen para cargarla</span>
            <small>Formatos soportados: JPG, PNG, WebP</small>
          </div>
          <img
            v-else
            :src="previewImage"
            alt="Vista previa"
            class="preview-image"
          />
        </div>

        <div v-if="previewImage" class="buttons">
          <button 
            class="btn analyze-btn" 
            :disabled="loading" 
            @click="startInference"
          >
            {{ loading ? 'Analizando...' : 'Iniciar análisis' }}
          </button>
          <button class="btn change-btn" @click="resetImage" :disabled="loading">
            Cambiar imagen
          </button>
        </div>
      </section>
      
      <!-- Error message -->
      <section v-if="error" class="error-section">
        <h2>Error:</h2>
        <p class="error-message">{{ error }}</p>
        <button v-if="error.includes('login')" @click="$router.push('/login')" class="btn login-btn">
          Ir al Login
        </button>
      </section>
      
      <!-- Results section -->
      <section v-if="result" class="result-section">
        <h2>Resultado del Análisis:</h2>
        <div v-if="result.generatedImgUrl" class="result-image-container">
          <img :src="result.generatedImgUrl" alt="Resultado del análisis" class="result-image"/>
        </div>
        <div class="result-details">
          <p><strong>Estado:</strong> Análisis completado exitosamente</p>
          <p><strong>Imagen procesada:</strong> {{ selectedFile?.name }}</p>
        </div>
      </section>
      
      <!-- Debug section -->
      <!-- <section v-if="debug && isDevelopment" class="debug-section">
        <h3>Información de Depuración</h3>
        <pre class="debug-content">{{ debug }}</pre>
      </section> -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '../../composables/use_auth.js'
import { useInference } from '../../composables/send_inference.js'

// Authentication
const { isLoggedIn, user, loading: authLoading, checkAuthStatus } = useAuth()

// File handling
const fileInput = ref(null)
const previewImage = ref(null)
const selectedFile = ref(null)

// Inference handling
const { loading, error, result, debug, handleInference } = useInference()

// Development mode check
const isDevelopment = computed(() => {
  return import.meta.env.MODE === 'development'
})

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
</script>

<style scoped>
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
  text-align: center;
}

.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.logo-image {
  max-width: 400px;
  width: 90%;
  height: auto;
  border-radius: 10px;
}

section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 800;
  color: #b22222;
}

.justify-text {
  text-align: justify;
}

.big-paragraph {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #555;
}

/* Authentication sections */
.auth-required, .loading-section {
  padding: 3rem 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.user-info {
  background: rgba(46, 204, 113, 0.1);
  padding: 0.8rem 1.2rem;
  border-radius: 8px;
  color: #27ae60;
  font-weight: 500;
  display: inline-block;
  margin-top: 1rem;
}

/* Upload section improvements */
.upload-box {
  min-height: 300px;
  border: 3px dashed #b22222;
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(178, 34, 34, 0.02);
  position: relative;
}

.upload-box:hover:not(.disabled) {
  border-color: #8B0000;
  background: rgba(178, 34, 34, 0.05);
  transform: scale(1.01);
}

.upload-box.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.placeholder {
  text-align: center;
  color: #666;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.placeholder span {
  font-size: 1.2rem;
  font-weight: 500;
  color: #b22222;
  display: block;
  margin-bottom: 0.5rem;
}

.placeholder small {
  color: #888;
  font-size: 0.9rem;
}

/* Error section */
.error-section {
  background: #ffe6e6;
  border: 2px solid #ff9999;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
}

.error-message {
  color: #cc0000;
  font-weight: 500;
  margin-bottom: 1rem;
}

/* Results section */
.result-section {
  background: #e8f5e8;
  border: 2px solid #90EE90;
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
}

.result-image-container {
  margin: 1.5rem 0;
}

.result-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 10px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.result-details {
  background: rgba(255,255,255,0.8);
  padding: 1rem;
  border-radius: 8px;
  text-align: left;
}

/* Debug section */
.debug-section {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  text-align: left;
}

.debug-content {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
}

.upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.upload-box {
  width: 600px;
  height: 400px;
  border: 2px dashed #b22222;
  border-radius: 12px;
  background-color: #f9f9f9;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
}

.upload-box:hover {
  background-color: #f0f0f0;
  transform: scale(1.02);
}

.placeholder {
  color: #555;
  font-size: 1rem;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  border-radius: 10px;
  object-fit: contain;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.buttons {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
}

.analyze-btn {
  background-color: #4caf50;
  color: white;
}

.analyze-btn:hover {
  background-color: #43a047;
}

.change-btn {
  background-color: #e53935;
  color: white;
}

.change-btn:hover {
  background-color: #c62828;
}

@media (max-width: 768px) {
  .upload-box {
    width: 90%;
    height: 300px;
  }
  .big-paragraph {
    font-size: 1rem;
  }
}
</style>
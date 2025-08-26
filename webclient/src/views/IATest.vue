<template>
  <div class="page-wrapper">

    <div class="logo-wrapper">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
    </div>

    <section class="hero-section">
      <h1 class="section-title">Análisis de Imágenes</h1>
      <p class="big-paragraph">
        Carga una imagen de frambuesa para iniciar el proceso de análisis con nuestra IA. 
      </p>
    </section>

    <section class="upload-section">
      <div class="upload-box" @click="triggerFileInput">
        <input
          type="file"
          ref="fileInput"
          accept="image/*"
          @change="onFileChange"
          style="display: none"
        />
        <div v-if="!previewImage" class="placeholder">
          Haz clic aquí o arrastra una imagen para cargarla
        </div>
        <img
          v-else
          :src="previewImage"
          alt="Vista previa"
          class="preview-image"
        />
      </div>

      <div v-if="previewImage" class="buttons">
        <button class="btn analyze-btn" @click="startAnalysis">Iniciar análisis</button>
        <button class="btn change-btn" @click="resetImage">Cambiar imagen</button>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)
const previewImage = ref(null)

function triggerFileInput() {
  fileInput.value.click()
}

function onFileChange(event) {
  const file = event.target.files[0]
  if (file && file.type.startsWith("image/")) {
    previewImage.value = URL.createObjectURL(file)
  }
}

function resetImage() {
  previewImage.value = null
  fileInput.value.value = ""
}

function startAnalysis() {
  alert("IA Test")
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
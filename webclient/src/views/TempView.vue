<template>
  <div class="temp-view">
    <h1>Temp View Inferencias</h1>
    <input type="file" @change="onFileChange" accept="image/*" />
    <button :disabled="!selectedFile || loading" @click="handleInference(selectedFile)">Enviar imagen</button>
    <div v-if="loading">Procesando...</div>
    <div v-if="error" style="color:red;">{{ error }}</div>
    <div v-if="result">
      <h2>Resultado:</h2>
      <img :src="result.generatedImgUrl" alt="Resultado" style="max-width: 400px;" v-if="result.generatedImgUrl"/>
      <pre>{{ result }}</pre>
    </div>
    <div v-if="debug">
      <h3>Debug Info</h3>
      <pre>{{ debug }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useInference } from '../composables/send_inference.js'

const selectedFile = ref(null)
const { loading, error, result, debug, handleInference } = useInference()

function onFileChange(e) {
  selectedFile.value = e.target.files[0]
  result.value = null
  error.value = ''
  debug.value = `Archivo seleccionado: ${selectedFile.value ? selectedFile.value.name : 'Ninguno'}`
}
</script>

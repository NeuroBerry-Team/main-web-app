<template>
  <div class="w-full min-h-screen max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 font-sans text-gray-800 flex flex-col gap-6 sm:gap-8 lg:gap-12 text-center">
    <!-- Authentication check -->
    <section v-if="!isLoggedIn && !authLoading" class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-slate-50 to-blue-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-4 sm:gap-6 lg:gap-8">
      <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-red-700">Acceso Requerido</h1>
      <p class="text-sm sm:text-base lg:text-lg leading-relaxed text-gray-600 px-2">
        Debes iniciar sesión para acceder a la herramienta de análisis de imágenes.
      </p>
      <router-link to="/login" class="inline-block px-4 py-2 sm:px-6 sm:py-3 bg-red-700 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-red-800 transition-all duration-300">Iniciar Sesión</router-link>
    </section>

    <!-- Loading authentication -->
    <section v-if="authLoading" class="p-4 sm:p-8 lg:p-12 bg-gradient-to-br from-slate-50 to-blue-100 rounded-lg sm:rounded-xl lg:rounded-2xl shadow-xl flex flex-col gap-4 sm:gap-6 lg:gap-8">
      <h1 class="text-xl sm:text-2xl lg:text-4xl font-extrabold text-red-700">Verificando autenticación...</h1>
    </section>

    <!-- Main content - only show if authenticated -->
    <div v-if="isLoggedIn" class="flex flex-col gap-6 sm:gap-8 lg:gap-12">
      <section class="flex flex-col gap-4 sm:gap-6 lg:gap-8">
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-red-700">Análisis de Imágenes</h1>
        <p class="text-sm sm:text-base lg:text-lg leading-relaxed text-gray-600 px-2 sm:px-0">
          Carga una imagen de frambuesa para iniciar el proceso de análisis con nuestra IA.
        </p>
        <p v-if="user?.role" class="inline-block break-words bg-green-50 px-3 py-2 sm:px-5 sm:py-3 rounded-lg text-green-700 font-medium text-xs sm:text-sm lg:text-base mt-2 lg:mt-4">
          Conectado como: <strong>{{ user.role }}</strong>
        </p>
      </section>

      <section class="flex flex-col items-center gap-4 sm:gap-6">
        <div class="w-full max-w-sm sm:max-w-lg lg:max-w-2xl border-2 sm:border-4 border-dashed border-red-700 rounded-xl sm:rounded-2xl bg-red-50/20 cursor-pointer flex justify-center items-center transition-all duration-300 hover:border-red-900 hover:bg-red-50/50 hover:scale-105 relative p-8 sm:p-10 lg:p-12" 
             @click="triggerFileInput" 
             :class="{ 
               'opacity-60 cursor-not-allowed hover:scale-100': loading, 
               'min-h-[240px] sm:min-h-[280px] lg:min-h-[320px]': !previewImage,
               'h-64 sm:h-80 lg:h-96': previewImage 
             }">
          <input
            type="file"
            ref="fileInput"
            accept="image/*"
            @change="onFileChange"
            style="display: none"
          />
          <div v-if="!previewImage" class="text-center text-gray-700 flex flex-col items-center justify-center w-full h-full">
            <div class="text-3xl sm:text-4xl lg:text-5xl mb-4 sm:mb-6">📁</div>
            <div class="flex flex-col items-center gap-2 sm:gap-3 max-w-[90%]">
              <span class="text-sm sm:text-base lg:text-lg font-medium text-red-700 leading-relaxed text-center">Haz clic aquí o arrastra una imagen para cargarla</span>
              <small class="text-gray-500 text-xs sm:text-sm leading-relaxed text-center">Formatos soportados: JPG, PNG, WebP</small>
            </div>
          </div>
          <img
            v-else
            :src="previewImage"
            alt="Vista previa"
            class="max-w-full max-h-full rounded-lg object-contain shadow-lg"
          />
        </div>

        <div v-if="previewImage" class="flex flex-col sm:flex-row gap-2 sm:gap-4 w-full max-w-md">
          <button 
            class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-green-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-green-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed" 
            :disabled="loading" 
            @click="startInference"
          >
            {{ loading ? 'Analizando...' : 'Iniciar análisis' }}
          </button>
          <button class="flex-1 px-4 py-2 sm:px-6 sm:py-3 bg-red-600 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-red-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed" 
                  @click="resetImage" 
                  :disabled="loading">
            Cambiar imagen
          </button>
        </div>
      </section>
      
      <!-- Error message -->
      <section v-if="error" class="bg-red-50 border-2 border-red-300 rounded-lg sm:rounded-xl p-4 sm:p-6 lg:p-8 text-center flex flex-col gap-4 sm:gap-6 lg:gap-8">
        <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-red-800">Error:</h2>
        <p class="text-red-700 font-medium text-sm sm:text-base mb-2 sm:mb-4 px-2">{{ error }}</p>
        <button v-if="error.includes('login')" 
                @click="$router.push('/login')" 
                class="inline-block px-4 py-2 sm:px-6 sm:py-3 bg-red-700 text-white text-sm sm:text-base font-bold rounded-lg hover:bg-red-800 transition-all duration-300">
          Ir al Login
        </button>
      </section>
      
      <!-- Results section -->
      <section v-if="result" class="bg-green-50 border-2 border-green-300 rounded-lg sm:rounded-xl lg:rounded-2xl p-4 sm:p-6 lg:p-8 text-center flex flex-col gap-4 sm:gap-6 lg:gap-8">
        <h2 class="text-lg sm:text-xl lg:text-2xl font-bold text-green-800">Resultado del Análisis:</h2>
        <div v-if="result.generatedImgUrl" class="my-3 sm:my-4 lg:my-6">
          <img :src="result.generatedImgUrl" alt="Resultado del análisis" class="max-w-full max-h-64 sm:max-h-80 lg:max-h-96 mx-auto rounded-lg shadow-lg"/>
        </div>
        <div class="bg-white/80 p-3 sm:p-4 rounded-lg text-left overflow-hidden">
          <p class="text-sm sm:text-base mb-2 break-words"><strong>Estado:</strong> Análisis completado exitosamente</p>
          <p class="text-sm sm:text-base break-words overflow-wrap-anywhere"><strong>Imagen procesada:</strong> <span class="break-all">{{ selectedFile?.name }}</span></p>
        </div>
      </section>
      
      <!-- Debug section -->
      <!-- <section v-if="debug && isDevelopment" class="bg-gray-50 border border-gray-300 rounded-lg p-4 text-left flex flex-col gap-8">
        <h3 class="text-lg font-semibold">Información de Depuración</h3>
        <pre class="bg-white border border-gray-200 rounded p-4 font-mono text-sm max-h-80 overflow-y-auto whitespace-pre-wrap">{{ debug }}</pre>
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
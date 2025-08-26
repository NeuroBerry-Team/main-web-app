<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-700 to-red-600 p-4">
    <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md transition-all duration-300">
      <div class="text-center mb-6">
        <img src="/NeuroBerry_Logo.png" alt="NeuroBerry" class="h-16 mx-auto mb-2" />
        <h1 class="text-2xl font-bold bg-gradient-to-r from-red-700 to-red-600 bg-clip-text text-transparent">NeuroBerry</h1>
      </div>

      <!-- Tabs -->
      <div class="flex bg-gray-50 rounded-xl p-1 mb-6">
        <button 
          :class="[
            'flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all duration-200',
            activeTab === 'login' 
              ? 'bg-white text-red-700 shadow-sm' 
              : 'text-gray-600 hover:text-red-700'
          ]"
          @click="activeTab = 'login'"
        >
          Iniciar Sesión
        </button>
        <button 
          :class="[
            'flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all duration-200',
            activeTab === 'register' 
              ? 'bg-white text-red-700 shadow-sm' 
              : 'text-gray-600 hover:text-red-700'
          ]"
          @click="activeTab = 'register'"
        >
          Registrarse
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="activeTab === 'login'" class="space-y-4" @submit.prevent="handleLogin">
        <h2 class="text-xl font-bold text-center text-gray-800 mb-4">Bienvenido</h2>
        
        <div v-if="loginError" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
          <div class="flex items-center">
            <span class="text-red-500 mr-2">⚠️</span>
            <p class="text-red-700 text-sm">{{ loginError }}</p>
          </div>
        </div>
        
        <div class="space-y-1">
          <label for="login-email" class="block text-sm font-semibold text-gray-700">Correo Electrónico</label>
          <input 
            id="login-email"
            type="email" 
            v-model="loginEmail" 
            placeholder="ejemplo@correo.com" 
            required 
            :disabled="loginLoading"
            class="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg focus:border-red-700 focus:ring-2 focus:ring-red-100 transition-colors duration-200 disabled:bg-gray-50"
          />
        </div>

        <div class="space-y-1">
          <label for="login-password" class="block text-sm font-semibold text-gray-700">Contraseña</label>
          <input 
            id="login-password"
            type="password" 
            v-model="loginPassword" 
            placeholder="Tu contraseña" 
            required 
            :disabled="loginLoading"
            class="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg focus:border-red-700 focus:ring-2 focus:ring-red-100 transition-colors duration-200 disabled:bg-gray-50"
          />
        </div>

        <button 
          type="submit" 
          :disabled="loginLoading" 
          class="w-full bg-gradient-to-r from-red-700 to-red-600 text-white py-2.5 px-4 rounded-lg font-semibold hover:from-red-800 hover:to-red-700 focus:ring-4 focus:ring-red-200 disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 mt-6"
        >
          <span v-if="loginLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          {{ loginLoading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
        </button>
        
        <p class="text-center text-gray-600 text-sm mt-4 hover:text-red-700 cursor-pointer transition-colors">¿Olvidaste tu contraseña?</p>
      </form>

      <!-- Registration Form -->
      <form v-if="activeTab === 'register'" class="space-y-4" @submit.prevent="handleRegister">
        <h2 class="text-xl font-bold text-center text-gray-800 mb-4">Crear Cuenta Nueva</h2>
        
        <div v-if="registerError" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
          <div class="flex items-center">
            <span class="text-red-500 mr-2">⚠️</span>
            <p class="text-red-700 text-sm">{{ registerError }}</p>
          </div>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-1">
            <label for="register-name" class="block text-sm font-semibold text-gray-700">Nombre</label>
            <input 
              id="register-name"
              type="text" 
              v-model="registerName" 
              placeholder="Tu nombre" 
              required 
              :disabled="registerLoading"
              class="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg focus:border-red-700 focus:ring-2 focus:ring-red-100 transition-colors duration-200 disabled:bg-gray-50"
            />
          </div>
          
          <div class="space-y-1">
            <label for="register-lastname" class="block text-sm font-semibold text-gray-700">Apellido</label>
            <input 
              id="register-lastname"
              type="text" 
              v-model="registerLastName" 
              placeholder="Tu apellido" 
              required 
              :disabled="registerLoading"
              class="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg focus:border-red-700 focus:ring-2 focus:ring-red-100 transition-colors duration-200 disabled:bg-gray-50"
            />
          </div>
        </div>

        <div class="space-y-1">
          <label for="register-email" class="block text-sm font-semibold text-gray-700">Correo Electrónico</label>
          <input 
            id="register-email"
            type="email" 
            v-model="registerEmail" 
            placeholder="ejemplo@correo.com" 
            required 
            :disabled="registerLoading"
            class="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg focus:border-red-700 focus:ring-2 focus:ring-red-100 transition-colors duration-200 disabled:bg-gray-50"
          />
        </div>

        <div class="space-y-1">
          <label for="register-password" class="block text-sm font-semibold text-gray-700">Contraseña</label>
          <input 
            id="register-password"
            type="password" 
            v-model="registerPassword" 
            placeholder="Mínimo 8 caracteres, con letras y números" 
            required 
            :disabled="registerLoading"
            class="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg focus:border-red-700 focus:ring-2 focus:ring-red-100 transition-colors duration-200 disabled:bg-gray-50"
          />
          <small class="text-gray-600 text-xs">Debe contener al menos 8 caracteres, una letra y un número</small>
        </div>

        <div class="space-y-1">
          <label for="register-confirm" class="block text-sm font-semibold text-gray-700">Confirmar Contraseña</label>
          <input 
            id="register-confirm"
            type="password" 
            v-model="registerConfirm" 
            placeholder="Repite tu contraseña" 
            required 
            :disabled="registerLoading"
            class="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg focus:border-red-700 focus:ring-2 focus:ring-red-100 transition-colors duration-200 disabled:bg-gray-50"
          />
        </div>

        <button 
          type="submit" 
          :disabled="registerLoading" 
          class="w-full bg-gradient-to-r from-red-700 to-red-600 text-white py-2.5 px-4 rounded-lg font-semibold hover:from-red-800 hover:to-red-700 focus:ring-4 focus:ring-red-200 disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 mt-6"
        >
          <span v-if="registerLoading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          {{ registerLoading ? 'Creando cuenta...' : 'Crear Cuenta' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCSRF } from '../composables/use_csrf.js'

const APIurl = import.meta.env.VITE_API_BASE_URL
const { makeSecureRequest } = useCSRF()

const activeTab = ref('login')

// Login state
const loginEmail = ref('')
const loginPassword = ref('')
const loginLoading = ref(false)
const loginError = ref('')

const handleLogin = async () => {
  if (loginLoading.value) return
  
  loginLoading.value = true
  loginError.value = ''
  
  try {
    const response = await fetch(`${APIurl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: loginEmail.value,
        passwd: loginPassword.value
      }),
      credentials: 'include'
    })
    
    if (!response.ok) {
      const errorData = await response.text()
      let errorMessage = 'Error al iniciar sesión'
      
      if (response.status === 401) {
        errorMessage = 'Email o contraseña incorrectos'
      } else if (response.status === 400) {
        errorMessage = 'Por favor verifica tu email y contraseña'
      } else {
        errorMessage = `Error del servidor: ${response.status}`
      }
      
      throw new Error(errorMessage)
    }
    
    const data = await response.json()
    
    if (data.loggedIn) {
      window.location.href = '/'
    } else {
      throw new Error('Error al iniciar sesión - respuesta inválida')
    }
    
  } catch (error) {
    loginError.value = error.message
  } finally {
    loginLoading.value = false
  }
}

// Register state
const registerName = ref('')
const registerLastName = ref('')
const registerEmail = ref('')
const registerPassword = ref('')
const registerConfirm = ref('')
const registerLoading = ref(false)
const registerError = ref('')

const handleRegister = async () => {
  if (registerLoading.value) return
  
  registerLoading.value = true
  registerError.value = ''
  
  // Basic validation
  if (!registerName.value || registerName.value.trim().length < 2) {
    registerError.value = 'El nombre debe tener al menos 2 caracteres'
    registerLoading.value = false
    return
  }

  if (!registerLastName.value || registerLastName.value.trim().length < 2) {
    registerError.value = 'El apellido debe tener al menos 2 caracteres'
    registerLoading.value = false
    return
  }
  
  if (registerPassword.value !== registerConfirm.value) {
    registerError.value = 'Las contraseñas no coinciden'
    registerLoading.value = false
    return
  }
  
  if (registerPassword.value.length < 8) {
    registerError.value = 'La contraseña debe tener al menos 8 caracteres'
    registerLoading.value = false
    return
  }
  
  try {
    const response = await makeSecureRequest(`${APIurl}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: registerName.value.trim(),
        lastName: registerLastName.value.trim(),
        email: registerEmail.value,
        password: registerPassword.value
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Clear form
      registerName.value = ''
      registerLastName.value = ''
      registerEmail.value = ''
      registerPassword.value = ''
      registerConfirm.value = ''
      
      // Show success message and switch to login
      alert(data.message || '¡Registro exitoso! Por favor inicia sesión.')
      activeTab.value = 'login'
      
    } else {
      let errorMessage = 'Error en el registro'
      
      try {
        const errorData = await response.json()
        errorMessage = errorData.message || errorData.error || `Error del servidor: ${response.status}`
      } catch (jsonError) {
        try {
          const errorText = await response.text()
          errorMessage = errorText || `Error del servidor: ${response.status}`
        } catch (textError) {
          errorMessage = `Error del servidor: ${response.status}`
        }
      }
      
      registerError.value = errorMessage
    }
    
  } catch (error) {
    let errorMessage = 'Error en el registro'
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      errorMessage = 'Error de conexión - por favor verifica tu conexión'
    } else if (error.message) {
      errorMessage = error.message
    }
    
    registerError.value = errorMessage
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
/* Custom styles if needed - Tailwind handles most styling */
</style>

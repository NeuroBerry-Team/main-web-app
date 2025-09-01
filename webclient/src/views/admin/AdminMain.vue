<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Admin Dashboard Header -->
    <section class="py-10 bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Panel de Administración</h1>
            <p class="text-gray-600 mt-1">
              Gestiona entrenamientos y usuarios del sistema
            </p>
          </div>
          <div class="flex items-center gap-3">
            <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {{ user?.role }}
            </span>
            <span class="text-sm text-gray-500">{{ user?.name || user?.username }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Navigation Tabs -->
    <section class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav class="flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm transition-all duration-200',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </nav>
      </div>
    </section>

    <!-- Tab Content -->
    <section class="flex-1">
      <!-- Training Management Tab -->
      <div v-if="activeTab === 'training'" class="py-6">
        <TrainingManager />
      </div>

      <!-- User Management Tab (Future) -->
      <div v-else-if="activeTab === 'users'" class="py-6">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="bg-white rounded-lg shadow p-8 text-center">
            <div class="text-6xl mb-4">👥</div>
            <h3 class="text-xl font-bold text-gray-700 mb-2">Gestión de Usuarios</h3>
            <p class="text-gray-500">Esta funcionalidad estará disponible próximamente.</p>
          </div>
        </div>
      </div>

      <!-- System Settings Tab (Future) -->
      <div v-else-if="activeTab === 'settings'" class="py-6">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="bg-white rounded-lg shadow p-8 text-center">
            <div class="text-6xl mb-4">⚙️</div>
            <h3 class="text-xl font-bold text-gray-700 mb-2">Configuración del Sistema</h3>
            <p class="text-gray-500">Esta funcionalidad estará disponible próximamente.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../../composables/use_auth.js'
import TrainingManager from './TrainingManager.vue'

// Composables
const { user, checkAuthStatus, isLoggedIn, isAdmin } = useAuth()

// State
const activeTab = ref('training')

// Available tabs
const tabs = ref([
  { id: 'training', label: 'Entrenamientos', icon: '🔄' },
  { id: 'users', label: 'Usuarios', icon: '👥' },
  { id: 'settings', label: 'Configuración', icon: '⚙️' }
])

// Lifecycle
onMounted(async () => {
  await checkAuthStatus()
})
</script>
<script setup>
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuth } from './composables/use_auth.js'
import { useCSRF } from './composables/use_csrf.js'
import NavBar from './components/NavBar.vue'

const { checkAuthStatus } = useAuth()
const { initializeCSRF } = useCSRF()

onMounted(async () => {
  await initializeCSRF()
  await checkAuthStatus()
})
</script>

<template>
  <div id="app" class="w-full min-h-screen flex flex-col font-poppins">
    <header
      class="fixed top-0 left-0 w-full bg-red-700 text-white py-4 flex justify-center shadow-lg z-[1000] transition-colors duration-300 hover:bg-red-600"
    >
      <div class="flex items-center justify-center gap-8 w-full max-w-5xl flex-wrap md:flex-col md:gap-2">
        <NavBar />
      </div>
    </header>

    <main class="w-full min-h-screen mt-[90px] p-8 box-border">
      <RouterView />
    </main>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap'); /*TODO: Change it to tailwind.config */
</style>
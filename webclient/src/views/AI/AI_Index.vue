<template>
    <h1 class="text-2xl font-bold mb-2">Hello world!</h1>
    <p class="mb-6 text-gray-700">This is the AI Index page.</p>
    <div class="flex gap-4 mb-8 justify-center">
      <router-link
        to="/AI/train"
        class="px-5 py-2 rounded-full bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition"
      >Train AI</router-link>
      <router-link
        to="/AI/inference"
        class="px-5 py-2 rounded-full bg-green-600 text-white font-semibold shadow hover:bg-green-700 transition"
      >Test AI</router-link>
    </div>
    <router-view />
</template>
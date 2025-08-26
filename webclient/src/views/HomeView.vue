<template>
  <div class="page-wrapper">
    <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo-image" />
  </div>
</template>

<script setup></script>

<style scoped>
.page-wrapper {
  width: 100%;
  min-height: calc(100vh - 6rem);
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  text-align: center;
  font-family: 'Poppins', sans-serif;
  color: #333;
  animation: fadeInUp 0.5s ease forwards;
}

h1 { font-size: 2rem; margin-bottom: 1rem; }
p { font-size: 1.2rem; line-height: 1.6; }

@keyframes fadeInUp {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
</style>
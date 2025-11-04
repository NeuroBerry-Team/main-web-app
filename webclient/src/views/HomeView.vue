<template>
  <div class="page-wrapper">
    <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="logo" />

    <h1 class="title">Bienvenido a NeuroBerry</h1>

    <p class="subtitle">
      Inteligencia Artificial para optimizar y potenciar tus cultivos.
    </p>
  </div>
</template>

<script setup>
</script>

<style scoped>
:root {
  --primary-red: #cc0000;
  --dark-red: #8b0000;
  --text-light: #f5f5f5;
  --accent-green: #2ecc71;
}

.page-wrapper {
  width: 100%; 
  min-height: 100vh;
  margin: 0;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(135deg, var(--dark-red) 0%, #3a0a0a 50%, #1a1a1a 100%);
  color: var(--text-light);
  overflow-x: hidden;
  box-sizing: border-box;
}
@media (min-width: 640px) {
  .page-wrapper {
    padding: 2rem;
  }
}

.logo, .title, .subtitle, .cta-button {
  opacity: 0;
  transform: translateY(30px);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logo {
  max-width: 400px;
  width: 70%;
  height: auto;
  margin-bottom: 2rem;
  filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5));
  animation: fadeInUp 0.8s ease forwards;
  animation-delay: 0.2s;
}

.title {
  font-size: clamp(3rem, 7vw, 4.5rem);
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-shadow: 3px 3px 10px rgba(0, 0, 0, 0.6);
  animation: fadeInUp 0.8s ease forwards;
  animation-delay: 0.5s;
}

.subtitle {
  font-size: clamp(1.2rem, 3vw, 1.6rem);
  max-width: 700px;
  line-height: 1.6;
  margin-bottom: 3rem;
  animation: fadeInUp 0.8s ease forwards;
  animation-delay: 0.8s;
}

.cta-button {
  padding: 18px 40px;
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
  background-color: var(--accent-green);
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 0.8s ease forwards;
  animation-delay: 1.1s;
}

.cta-button:hover {
  transform: translateY(-7px);
  box-shadow: 0 10px 30px rgba(46, 204, 113, 0.5);
  background-color: #27ae60;
}

@media (max-width: 600px) {
  .logo {
    max-width: 250px;
    margin-bottom: 1.5rem;
  }
  .title {
    font-size: clamp(2rem, 8vw, 3rem);
  }
  .subtitle {
    font-size: clamp(0.9rem, 3.5vw, 1.2rem);
    max-width: 90%;
  }
  .cta-button {
    padding: 12px 25px;
    font-size: 1rem;
  }
}
</style>
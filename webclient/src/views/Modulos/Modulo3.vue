<template>
  <div class="page-wrapper">
    <section class="hero-section animated-item">
      <h1 class="hero-title">Módulo III: Sistemas Distribuidos</h1>
      <p class="hero-text">
        La magia detrás de la accesibilidad: cómo logramos que una potente IA esté disponible en cualquier dispositivo a través de una arquitectura web moderna y escalable.
      </p>
    </section>

    <div class="content-grid">
      <div class="content-section animated-item" style="animation-delay: 0.1s;">
        <div class="section-icon">🌐</div>
        <h2 class="section-title">Arquitectura Cliente-Servidor</h2>
        <p class="section-text">
          El sistema está diseñado para separar las responsabilidades. El **cliente** (tu navegador) se encarga de mostrar la interfaz, mientras que el **servidor** (nuestra infraestructura) realiza todo el trabajo pesado. Esto garantiza que la aplicación sea rápida y no consuma recursos de tu dispositivo.
        </p>
      </div>

      <div class="content-section animated-item" style="animation-delay: 0.2s;">
        <div class="section-icon">🧩</div>
        <h2 class="section-title">Tres Servidores, Un Sistema</h2>
        <p class="section-text">
          Nuestra arquitectura distribuida se compone de tres servicios principales que trabajan en conjunto:
          <ul>
            <li><strong>Frontend (Vue.js):</strong> La interfaz visual con la que interactúas.</li>
            <li><strong>Backend (Flask):</strong> El cerebro que gestiona usuarios, datos y peticiones.</li>
            <li><strong>Servidor de IA (FastAPI):</strong> Un servicio especializado y optimizado para ejecutar el modelo YOLOv8 y procesar las imágenes a alta velocidad.</li>
          </ul>
        </p>
         
      </div>

      <div class="content-section animated-item" style="animation-delay: 0.3s;">
        <div class="section-icon">🚀</div>
        <h2 class="section-title">Escalable y Accesible</h2>
        <p class="section-text">
          Gracias a esta arquitectura, NeuroBerry es:
           <ul>
            <li><strong>Accesible:</strong> Puedes usar la herramienta desde cualquier lugar y dispositivo con conexión a internet, no solo en una red local.</li>
            <li><strong>Escalable:</strong> El sistema está preparado para atender a múltiples usuarios enviando análisis al mismo tiempo sin colapsar.</li>
            <li><strong>Eficiente:</strong> Al dedicar un servidor exclusivamente a la IA, garantizamos los mejores tiempos de respuesta posibles.</li>
          </ul>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
/* Estilos idénticos al Módulo 1 para consistencia */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 7rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #fff;
}
.hero-section {
  max-width: 1200px;
  margin: 0 auto 3rem auto;
  background: linear-gradient(45deg, #b91c1c, #7f1d1d);
  color: white;
  padding: 3rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(185, 28, 28, 0.25);
}
.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.hero-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.2rem;
  margin-top: 1rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}
.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}
.content-section {
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07);
  padding: 2.5rem;
  text-align: center;
  border: 1px solid #e5e7eb;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}
.content-section:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px -5px rgba(0,0,0,0.1);
}
.section-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
}
.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #b22222;
  margin-bottom: 1rem;
}
.section-text {
  font-size: 1rem;
  line-height: 1.7;
  color: #555;
  flex-grow: 1;
}
.section-text ul {
  text-align: left;
  list-style-position: inside;
  margin-top: 1rem;
}
.animated-item {
  opacity: 0;
  animation: fadeInUp 0.7s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
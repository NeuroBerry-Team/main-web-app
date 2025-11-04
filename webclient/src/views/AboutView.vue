<template>
  <div class="page-wrapper">
    
    <section class="hero-section animated-item">
      <img src="/NeuroBerry_horizontal.png" alt="NeuroBerry Logo" class="hero-logo" />
      <h1 class="hero-title">🍓 Inteligencia Artificial para la Madurez de Frambuesas</h1>
      <p class="hero-text">
        Una solución de Visión por Computadora para automatizar la identificación del estado de madurez, optimizando la cosecha, mejorando la calidad y reduciendo costos en el sector agrícola.
      </p>
    </section>

    <section class="content-section animated-item" style="animation-delay: 0.1s;">
      <h2 class="section-title">Nuestro Proceso de Desarrollo</h2>
      <div class="two-column-grid">
        <div class="text-content">
          <h3>Dataset Propio en Campo</h3>
          <p>Capturamos más de 3,000 imágenes en condiciones reales (diferentes horas, invernaderos y ángulos) para crear un conjunto de datos robusto y representativo.</p>
          
          <h3>Etiquetado con Label Studio</h3>
          <p>Anotamos miles de instancias de frambuesas, clasificándolas en 5 clases estandarizadas (de C1 a C5) para enseñar al modelo a diferenciar cada etapa de madurez.</p>
          
          <h3>Modelo de IA</h3>
          <p>Utilizamos una red de detección de objetos de última generación (YOLOv8) para localizar y clasificar con alta precisión cada fruto en las imágenes.</p>
        </div>
        <div class="image-content">
          <img src="/frambuesas_1.jpg" alt="Investigación y desarrollo de NeuroBerry" />
        </div>
      </div>
    </section>

    <section class="content-section animated-item" style="animation-delay: 0.2s;">
      <h2 class="section-title">Resultados y Beneficios</h2>
      <div class="card-grid">
        <div class="feature-card">
          <div class="feature-icon">🎯</div>
          <h3 class="feature-title">Optimización</h3>
          <p class="feature-text">Mejora la precisión y objetividad en la identificación de la madurez, optimizando el momento de la cosecha.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">💰</div>
          <h3 class="feature-title">Reducción de Costos</h3>
          <p class="feature-text">Disminuye la dependencia de la mano de obra y reduce la variabilidad humana en la clasificación de los frutos.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">📈</div>
          <h3 class="feature-title">Mejora Continua</h3>
          <p class="feature-text">El sistema está diseñado para mejorar constantemente a través de reentrenamiento y nuevas técnicas como el aprendizaje activo.</p>
        </div>
      </div>
    </section>

    <section class="content-section animated-item" style="animation-delay: 0.3s;">
       <h2 class="section-title">Diagrama de Bloques del Sistema</h2>
       <div class="diagram-container">
         <img src="/diagrama_bloques.png" alt="Diagrama de bloques del sistema NeuroBerry" />
       </div>
    </section>
  </div>
</template>

<script setup>
// No se necesita lógica de script para esta vista estática
</script>

<style scoped>
/* --- Estilos Generales de la Página --- */
.page-wrapper {
  width: 100%;
  min-height: 100vh;
  padding: 1rem;
  padding-top: 6rem;
  font-family: 'Poppins', sans-serif;
  color: #333;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  overflow-x: hidden;
}
@media (min-width: 640px) {
  .page-wrapper {
    padding: 2rem;
    padding-top: 7rem;
    gap: 3rem;
  }
}

/* --- Encabezado Hero --- */
.hero-section {
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(45deg, #b91c1c, #7f1d1d);
  color: white;
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(185, 28, 28, 0.25);
  overflow-x: hidden;
}
@media (min-width: 768px) {
  .hero-section {
    padding: 3rem;
  }
}
.hero-logo {
  max-width: 300px;
  width: 80%;
  height: auto;
  margin: 0 auto 1.5rem auto;
}
@media (min-width: 768px) {
  .hero-logo {
    max-width: 400px;
    margin: 0 auto 2rem auto;
  }
}
.hero-title {
  font-size: 1.5rem;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
@media (min-width: 640px) {
  .hero-title {
    font-size: 2rem;
  }
}
@media (min-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
}
.hero-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
  margin-top: 1rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .hero-text {
    font-size: 1.2rem;
  }
}

/* --- Secciones de Contenido --- */
.content-section {
  max-width: 1200px;
  margin: 0 auto;
  background-color: #fff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.07);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  overflow-x: hidden;
}
@media (min-width: 768px) {
  .content-section {
    padding: 2.5rem;
  }
}
.section-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #b22222;
  margin-bottom: 1.5rem;
  text-align: center;
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}
@media (min-width: 640px) {
  .section-title {
    font-size: 1.8rem;
  }
}
@media (min-width: 768px) {
  .section-title {
    font-size: 2.2rem;
    margin-bottom: 2rem;
  }
}

/* --- Layout de Dos Columnas --- */
.two-column-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
}
@media (min-width: 768px) {
  .two-column-grid {
    grid-template-columns: 1fr 1fr;
    gap: 2.5rem;
  }
}
.text-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  text-align: left;
}
@media (min-width: 768px) {
  .text-content {
    gap: 1.5rem;
  }
}
.text-content h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .text-content h3 {
    font-size: 1.25rem;
  }
}
.text-content p {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #555;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .text-content p {
    font-size: 1rem;
  }
}
.image-content img {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

/* --- Tarjetas de Características --- */
.card-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}
@media (min-width: 640px) {
  .card-grid {
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr));
    gap: 2rem;
  }
}
.feature-card {
  background-color: #f9fafb;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  text-align: center;
  overflow-x: hidden;
  word-wrap: break-word;
}
@media (min-width: 768px) {
  .feature-card {
    padding: 2rem;
  }
}
.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px -5px rgba(0,0,0,0.08);
}
.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}
.feature-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #b22222;
  margin-bottom: 0.75rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .feature-title {
    font-size: 1.25rem;
  }
}
.feature-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #666;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
@media (min-width: 768px) {
  .feature-text {
    font-size: 1rem;
  }
}

/* --- Diagrama --- */
.diagram-container {
  background-color: #f9fafb;
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid #e5e7eb;
}
.diagram-container img {
  width: 100%;
  max-width: 800px;
  height: auto;
  margin: 0 auto;
}

/* --- Animaciones --- */
.animated-item {
  opacity: 0;
  animation: fadeInUp 0.7s ease-out forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* --- Responsividad --- */
@media (max-width: 768px) {
  .two-column-grid {
    grid-template-columns: 1fr;
  }
  .image-content {
    order: -1;
  }
}
</style>
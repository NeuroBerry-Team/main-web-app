<template>
  <div class="page-wrapper">
    <section class="hero-section animated-item">
      <h1 class="hero-title">Módulo I: Arquitectura y Programación de Sistemas</h1>
      <p class="hero-text">
        La base sobre la que se construyó NeuroBerry: una metodología de trabajo ágil, una arquitectura tecnológica moderna y un diseño planificado para resolver las necesidades del sector agrícola.
      </p>
    </section>

    <div class="content-grid">
      <div class="content-section animated-item" style="animation-delay: 0.1s;">
        <div class="section-icon">🔄</div>
        <h2 class="section-title">Metodología Ágil y Modular</h2>
        <p class="section-text">
          Se adoptó un enfoque de desarrollo **iterativo e incremental**. Esto significa que el proyecto se dividió en módulos (adquisición de imágenes, procesamiento, etc.) que se desarrollaron en ciclos cortos. Cada ciclo incluía planificación, desarrollo, pruebas y retroalimentación, permitiendo validar los avances de forma temprana directamente en campo y mejorar continuamente.
        </p>
        
      </div>

      <div class="content-section animated-item" style="animation-delay: 0.2s;">
        <div class="section-icon">🏗️</div>
        <h2 class="section-title">Arquitectura Full-Stack</h2>
        <p class="section-text">
          La tecnología se eligió para maximizar la eficiencia y accesibilidad:
          <ul>
            <li><strong>Frontend (Cliente):</strong> Se utilizó **Vue.js** para crear una interfaz de usuario rápida, interactiva y fácil de usar sin necesidad de conocimientos técnicos.</li>
            <li><strong>Backend (Servidor):</strong> Se programó en **Python** con el framework Flask, ideal para gestionar la lógica de negocio, los usuarios y la comunicación con la base de datos.</li>
          </ul>
        </p>
        
      </div>
      
      <div class="content-section animated-item" style="animation-delay: 0.3s;">
        <div class="section-icon">🗃️</div>
        <h2 class="section-title">Diseño y Base de Datos</h2>
        <p class="section-text">
          Antes de programar, se utilizaron **diagramas de casos de uso** para modelar el sistema y asegurar que cumpliera todos los requerimientos. Se implementó una base de datos para gestionar de forma segura la información de usuarios, los resultados de los análisis y las referencias a las imágenes almacenadas.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
/* Estilos coherentes con el resto de la aplicación */
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
/**
 * AR Visuals — Helpers para construir entornos espaciales 3D con A-Frame
 */

const ARVisuals = {

  /**
   * Crea el skybox espacial: esfera gigante + estrellas + nebulosas
   */
  createSpaceSkybox(scene) {
    const skybox = document.createElement('a-sphere');
    skybox.setAttribute('id', 'space-skybox');
    skybox.setAttribute('radius', '100');
    skybox.setAttribute('material',
      'shader: flat; side: back; color: #0a0e27;');
    scene.appendChild(skybox);

    this.createStars(scene, 200);
    this.createNebulae(scene);

    return skybox;
  },

  /**
   * Estrellas distribuidas en la esfera celeste con efecto twinkle
   */
  createStars(scene, count = 200) {
    const container = document.createElement('a-entity');
    container.setAttribute('id', 'stars-container');

    for (let i = 0; i < count; i++) {
      const star = document.createElement('a-sphere');

      const theta  = Math.random() * Math.PI * 2;
      const phi    = Math.acos(2 * Math.random() - 1);
      const radius = 80 + Math.random() * 15;

      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);

      star.setAttribute('position', `${x} ${y} ${z}`);
      star.setAttribute('radius', 0.1 + Math.random() * 0.3);

      const colors = ['#ffffff', '#e0f2fe', '#fef3c7', '#dbeafe'];
      const color  = colors[Math.floor(Math.random() * colors.length)];
      star.setAttribute('material',
        `shader: flat; color: ${color}; emissive: ${color}; emissiveIntensity: 1`);

      if (Math.random() < 0.3) {
        star.setAttribute('animation',
          `property: material.opacity; from: 0.4; to: 1; ` +
          `dur: ${1500 + Math.random() * 2000}; dir: alternate; loop: true`);
      }

      container.appendChild(star);
    }

    scene.appendChild(container);
  },

  /**
   * Nebulosas de color para dar profundidad atmosférica
   */
  createNebulae(scene) {
    const nebulae = [
      { color: '#ec4899', position: '-30 10 -50', opacity: 0.15 },
      { color: '#8b5cf6', position: '40 -5 -60',  opacity: 0.20 },
      { color: '#06b6d4', position: '0 25 -70',   opacity: 0.10 },
    ];

    nebulae.forEach(n => {
      const neb = document.createElement('a-circle');
      neb.setAttribute('radius', '20');
      neb.setAttribute('position', n.position);
      neb.setAttribute('material',
        `shader: flat; color: ${n.color}; opacity: ${n.opacity}; transparent: true; side: double`);
      neb.setAttribute('look-at', '[camera]');
      scene.appendChild(neb);
    });
  },

  /**
   * Iluminación dramática del espacio
   */
  setupLighting(scene) {
    const ambient = document.createElement('a-light');
    ambient.setAttribute('type', 'ambient');
    ambient.setAttribute('color', '#1e1b4b');
    ambient.setAttribute('intensity', '0.4');
    scene.appendChild(ambient);

    const sun = document.createElement('a-light');
    sun.setAttribute('type', 'point');
    sun.setAttribute('color', '#fbbf24');
    sun.setAttribute('intensity', '0.8');
    sun.setAttribute('position', '10 15 -10');
    scene.appendChild(sun);

    const fill = document.createElement('a-light');
    fill.setAttribute('type', 'directional');
    fill.setAttribute('color', '#8b5cf6');
    fill.setAttribute('intensity', '0.3');
    fill.setAttribute('position', '-10 5 5');
    scene.appendChild(fill);
  },

  /**
   * Asteroide (dodecaedro con rotación lenta)
   */
  createAsteroid(position, options = {}) {
    const asteroid = document.createElement('a-entity');
    asteroid.setAttribute('position', position);

    const radius = options.radius || (0.25 + Math.random() * 0.15);
    const color  = options.color  || '#8b6f47';

    const body = document.createElement('a-dodecahedron');
    body.setAttribute('radius', radius);
    body.setAttribute('material',
      `color: ${color}; roughness: 0.9; metalness: 0.1; emissive: ${color}; emissiveIntensity: 0.1`);
    asteroid.appendChild(body);

    asteroid.setAttribute('animation__rot',
      `property: rotation; to: 360 720 360; loop: true; ` +
      `dur: ${4000 + Math.random() * 3000}; easing: linear`);

    return asteroid;
  },

  /**
   * Planeta con halo brillante
   */
  createPlanet(position, color = '#06b6d4', radius = 0.35) {
    const planet = document.createElement('a-entity');
    planet.setAttribute('position', position);

    const body = document.createElement('a-sphere');
    body.setAttribute('radius', radius);
    body.setAttribute('material',
      `color: ${color}; emissive: ${color}; emissiveIntensity: 0.4; roughness: 0.5`);
    planet.appendChild(body);

    const halo = document.createElement('a-ring');
    halo.setAttribute('radius-inner', radius * 1.1);
    halo.setAttribute('radius-outer', radius * 1.5);
    halo.setAttribute('material',
      `shader: flat; color: ${color}; opacity: 0.3; transparent: true; side: double`);
    halo.setAttribute('look-at', '[camera]');
    planet.appendChild(halo);

    return planet;
  },

  /**
   * Satélite con paneles solares y rotación
   */
  createSatellite(position) {
    const sat = document.createElement('a-entity');
    sat.setAttribute('position', position);

    const body = document.createElement('a-box');
    body.setAttribute('width', '0.3');
    body.setAttribute('height', '0.2');
    body.setAttribute('depth', '0.2');
    body.setAttribute('material',
      'color: #6b7280; emissive: #4b5563; emissiveIntensity: 0.2; metalness: 0.8; roughness: 0.4');
    sat.appendChild(body);

    ['-0.4 0 0', '0.4 0 0'].forEach(pos => {
      const panel = document.createElement('a-plane');
      panel.setAttribute('width', '0.5');
      panel.setAttribute('height', '0.15');
      panel.setAttribute('position', pos);
      panel.setAttribute('material', 'color: #1e40af; metalness: 0.5; roughness: 0.3');
      sat.appendChild(panel);
    });

    const antenna = document.createElement('a-cylinder');
    antenna.setAttribute('radius', '0.02');
    antenna.setAttribute('height', '0.3');
    antenna.setAttribute('position', '0 0.25 0');
    antenna.setAttribute('material', 'color: #9ca3af');
    sat.appendChild(antenna);

    sat.setAttribute('animation__rot',
      'property: rotation; to: 0 360 0; loop: true; dur: 6000; easing: linear');

    return sat;
  },

  /**
   * Construye el entorno espacial completo (alias unificado para el layout)
   */
  buildSpaceEnvironment(scene) {
    this.createSpaceSkybox(scene);
    this.setupLighting(scene);
    this.createDistantSun(scene);
  },

  /**
   * Alias de createStars con más conteo por defecto (compatibilidad spec)
   */
  createStarfield(scene, count = 300) {
    this.createStars(scene, count);
  },

  /**
   * Sol distante visible como esfera brillante con halo
   */
  createDistantSun(scene) {
    const sun = document.createElement('a-entity');
    sun.setAttribute('id', 'distant-sun');
    sun.setAttribute('position', '30 20 -50');

    const core = document.createElement('a-sphere');
    core.setAttribute('radius', '3');
    core.setAttribute('material',
      'shader: flat; color: #fef3c7; emissive: #fbbf24; emissiveIntensity: 1');
    sun.appendChild(core);

    const halo = document.createElement('a-ring');
    halo.setAttribute('radius-inner', '3.2');
    halo.setAttribute('radius-outer', '5.5');
    halo.setAttribute('material',
      'shader: flat; color: #fbbf24; opacity: 0.3; transparent: true; side: double');
    halo.setAttribute('look-at', '[camera]');
    sun.appendChild(halo);

    scene.appendChild(sun);
    return sun;
  },

  /**
   * Feedback visual al hacer click (anillo que se expande en pantalla)
   */
  createClickFeedback(screenX, screenY, color = '#fbbf24') {
    const el = document.createElement('div');
    el.className = 'ar-click-feedback';
    el.style.left  = (screenX - 30) + 'px';
    el.style.top   = (screenY - 30) + 'px';
    el.style.borderColor = color;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 600);
  },

  /**
   * Explosión espacial: 8 partículas que se expanden y desvanecen
   */
  createExplosion(position, scene, color = '#fbbf24') {
    const explosion = document.createElement('a-entity');
    explosion.setAttribute('position', position);

    for (let i = 0; i < 8; i++) {
      const particle = document.createElement('a-sphere');
      particle.setAttribute('radius', '0.05');
      particle.setAttribute('material',
        `shader: flat; color: ${color}; emissive: ${color}; emissiveIntensity: 1`);

      const angle   = (Math.PI * 2 / 8) * i;
      const tx = Math.cos(angle);
      const ty = Math.sin(angle);
      const tz = (Math.random() - 0.5) * 0.5;

      particle.setAttribute('animation',
        `property: position; to: ${tx} ${ty} ${tz}; dur: 600; easing: easeOutQuad`);
      particle.setAttribute('animation__fade',
        'property: material.opacity; from: 1; to: 0; dur: 600');

      explosion.appendChild(particle);
    }

    scene.appendChild(explosion);
    setTimeout(() => explosion.remove(), 700);
  },
};

window.ARVisuals = ARVisuals;

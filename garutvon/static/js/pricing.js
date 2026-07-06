(() => {
  const card = document.querySelector("[data-pricing-3d]");
  if (!card || !window.THREE) return;

  const canvas = card.querySelector(".pricing-3d-canvas");
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.z = 5;

  const group = new THREE.Group();
  scene.add(group);

  const body = new THREE.Mesh(
    new THREE.BoxGeometry(1.95, 1.35, 0.22, 8, 8, 2),
    new THREE.MeshStandardMaterial({
      color: 0xf5f5f5,
      metalness: 0.2,
      roughness: 0.36,
      transparent: true,
      opacity: 0.9
    })
  );
  group.add(body);

  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(1.26, 0.018, 12, 92),
    new THREE.MeshBasicMaterial({ color: 0xbdbdbd, transparent: true, opacity: 0.75 })
  );
  ring.rotation.x = Math.PI / 2.6;
  group.add(ring);

  const nodes = [];
  const nodeGeometry = new THREE.SphereGeometry(0.055, 20, 20);
  const nodeMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.1, roughness: 0.25 });
  for (let index = 0; index < 10; index += 1) {
    const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
    node.userData.angle = (Math.PI * 2 * index) / 10;
    node.userData.radius = 1.3 + (index % 2) * 0.18;
    nodes.push(node);
    group.add(node);
  }

  scene.add(new THREE.AmbientLight(0xffffff, 1.7));
  const key = new THREE.DirectionalLight(0xffffff, 2.2);
  key.position.set(2, 3, 4);
  scene.add(key);

  let targetTiltX = 0;
  let targetTiltY = 0;
  let hoverBoost = 0;

  const resize = () => {
    const rect = card.getBoundingClientRect();
    renderer.setSize(rect.width, rect.height, false);
    camera.aspect = rect.width / rect.height;
    camera.updateProjectionMatrix();
  };

  card.addEventListener("pointermove", (event) => {
    const rect = card.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    targetTiltY = x * 0.75;
    targetTiltX = -y * 0.45;
    hoverBoost = 1;
  });

  card.addEventListener("pointerleave", () => {
    targetTiltX = 0;
    targetTiltY = 0;
    hoverBoost = 0;
  });

  const animate = (time) => {
    const seconds = time * 0.001;
    group.rotation.x += (targetTiltX - group.rotation.x) * 0.08;
    group.rotation.y += (targetTiltY + seconds * 0.18 - group.rotation.y) * 0.06;
    group.rotation.z = Math.sin(seconds * 1.4) * 0.04;
    group.scale.setScalar(1 + hoverBoost * 0.08);
    ring.rotation.z = seconds * (0.8 + hoverBoost * 0.9);

    nodes.forEach((node, index) => {
      const angle = node.userData.angle + seconds * (0.65 + index * 0.015);
      node.position.set(Math.cos(angle) * node.userData.radius, Math.sin(angle) * 0.42, Math.sin(angle) * node.userData.radius * 0.4);
    });

    renderer.render(scene, camera);
    window.requestAnimationFrame(animate);
  };

  resize();
  window.addEventListener("resize", resize);
  window.requestAnimationFrame(animate);
})();

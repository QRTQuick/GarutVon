(function(){
  const container = document.getElementById('logo-3d-container');
  if(!container) return;

  let width = container.clientWidth || 640;
  let height = container.clientHeight || 480;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  container.appendChild(renderer.domElement);

  const ambient = new THREE.AmbientLight(0xffffff, 0.85);
  scene.add(ambient);
  const dir = new THREE.DirectionalLight(0xffffff, 0.9);
  dir.position.set(5,10,7);
  scene.add(dir);

  camera.position.set(0, 0, 12);

  let logoMesh = null;

  function createPlane(texture){
    const aspect = (texture.image && texture.image.width && texture.image.height) ? texture.image.width/texture.image.height : 1;
    const heightPlane = 6.0;
    const widthPlane = heightPlane * aspect;
    const geom = new THREE.PlaneGeometry(widthPlane, heightPlane, 1, 1);
    const mat = new THREE.MeshStandardMaterial({ map: texture, transparent: true, depthWrite: false });
    logoMesh = new THREE.Mesh(geom, mat);
    logoMesh.position.set(1.8, -0.6, -1.8);
    logoMesh.rotation.set(-0.06, -0.6, 0);
    scene.add(logoMesh);
  }

  const loader = new THREE.TextureLoader();
  loader.crossOrigin = '';
  loader.load('/static/images/ist-logo.png',
    function(tex){ createPlane(tex); },
    undefined,
    function(){
      // fallback to favicon if custom image not present
      loader.load('/static/icons/favicon.svg', function(tex){ createPlane(tex); });
    }
  );

  function onResize(){
    width = container.clientWidth || window.innerWidth;
    height = container.clientHeight || window.innerHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }
  window.addEventListener('resize', onResize, { passive: true });

  let t = 0;
  function animate(){
    requestAnimationFrame(animate);
    t += 0.01;
    if(logoMesh){
      logoMesh.rotation.y = Math.sin(t * 0.6) * 0.35 - 0.6;
      logoMesh.rotation.x = Math.sin(t * 0.4) * 0.08 - 0.06;
      logoMesh.position.y = Math.sin(t * 0.6) * 0.15 - 0.6;
    }
    renderer.render(scene, camera);
  }
  animate();
})();

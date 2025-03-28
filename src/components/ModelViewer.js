import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { CSSTransition } from 'react-transition-group';

const ModelViewer = () => {
  const mountRef = useRef(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [show, setShow] = useState(true);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);

  const runOptimization = async (inputPath) => {
    try {
      setIsOptimizing(true);
      await ipcRenderer.invoke('run-optimization', {
        inputPath,
        outputPath: 'optimized_model.stl'
      });
      console.log('Optimization completed');
    } catch (error) {
      console.error('Optimization failed:', error);
    } finally {
      setIsOptimizing(false);
    }
  };

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!mountRef.current) return;
      const width = mountRef.current.clientWidth;
      const height = mountRef.current.clientHeight;
      setSize({ width, height });

      if (cameraRef.current && rendererRef.current) {
        cameraRef.current.aspect = width / height;
        cameraRef.current.updateProjectionMatrix();
        rendererRef.current.setSize(width, height);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  // Setup THREE.js scene
  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(75, size.width / size.height, 0.1, 1000);
    camera.position.z = 5;
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });

    // Fix: Ensure `window.devicePixelRatio` is available
    const pixelRatio = typeof window !== 'undefined' && window.devicePixelRatio ? window.devicePixelRatio : 1;
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(size.width, size.height);
    rendererRef.current = renderer;

    if (mountRef.current) {
      mountRef.current.appendChild(renderer.domElement);
    }

    // Controls setup
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 3;
    controls.maxDistance = 10;
    controlsRef.current = controls;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);

    // Example cube mesh
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshPhongMaterial({ 
      color: 0x00ff00,
      flatShading: true
    });
    const cube = new THREE.Mesh(geometry, material);
    scene.add(cube);

    // Animation loop
    let animationFrameId;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      cube.rotation.x += 0.01;
      cube.rotation.y += 0.01;
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Cleanup function
    return () => {
      cancelAnimationFrame(animationFrameId);

      if (scene) {
        scene.traverse((object) => {
          if (object.geometry) object.geometry.dispose();
          if (object.material) {
            if (Array.isArray(object.material)) {
              object.material.forEach(material => material.dispose());
            } else {
              object.material.dispose();
            }
          }
        });
      }

      if (controls) {
        controls.dispose();
      }

      if (renderer) {
        if (mountRef.current) {
          mountRef.current.removeChild(renderer.domElement);
        }
        renderer.dispose();
      }
    };
  }, [size.width, size.height]);

  return (
    <div className="model-viewer-container">
      <CSSTransition
        in={show}
        timeout={300}
        classNames="fade"
        unmountOnExit
      >
        <div 
          ref={mountRef} 
          className="model-viewer" 
          style={{ 
            width: '100%', 
            height: 'calc(100vh - 60px)',
            position: 'relative'
          }}
        />
      </CSSTransition>
      <button 
        className="optimize-button"
        onClick={() => runOptimization('input_model.stl')}
        disabled={isOptimizing}
      >
        {isOptimizing ? 'Optimizing...' : 'Optimize Model'}
      </button>
    </div>
  );
};

export default ModelViewer;
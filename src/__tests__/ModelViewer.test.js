import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
// import { useTheme } from 'next-themes'; // Removed next-themes
// import { cn } from "@/lib/utils"; // Removed "@/lib/utils" import
import { render } from '@testing-library/react';

// Mock the cn function directly within the test file
const cn = (...classes) => classes.filter(Boolean).join(' ');

const ModelViewer = ({ modelSrc, className }) => {
    const mountRef = useRef(null);
    // const { theme } = useTheme(); // Removed theme
    const theme = 'light'; //  default theme for testing
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Ensure the ref is available.  If not, early return.
        if (!mountRef.current) return;

        let scene, camera, renderer, controls;
        let isMounted = true; // Track component lifecycle

        const container = mountRef.current;
        const width = container.clientWidth;
        const height = container.clientHeight;

        // Scene setup
        scene = new THREE.Scene();

        // Camera setup
        camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        camera.position.z = 5;

        try {
            // Renderer setup
            renderer = new THREE.WebGLRenderer({
                antialias: true,
                alpha: true
            });
            renderer.setSize(width, height);
            container.appendChild(renderer.domElement);
        } catch (e) {
            console.error("Error creating WebGL renderer:", e);
            setError("Error creating WebGL context. Your browser may not support WebGL.");
            setLoading(false);
            return; // IMPORTANT: Exit the useEffect if WebGL fails
        }


        // Controls setup
        controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true; // Add damping for smoother interaction
        controls.dampingFactor = 0.1;
        controls.rotateSpeed = 0.5;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040); // Soft white light
        scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0xffffff, 1);
        pointLight.position.set(5, 5, 5);
        scene.add(pointLight);


        // Function to handle loading of the model.
        const loadModel = (url) => {
            setLoading(true);
            setError(null); // Clear any previous errors.

            let loader;
            if (url.endsWith('.gltf') || url.endsWith('.glb')) {
                loader = new THREE.GLTFLoader();
            } else if (url.endsWith('.obj')) {
                loader = new THREE.OBJLoader();
            } else {
                const errorMsg = "Unsupported model format.  Please use .gltf, .glb, or .obj.";
                console.error(errorMsg);
                setError(errorMsg);
                setLoading(false);
                return; // Stop loading if format is unsupported.
            }

            loader.load(
                url,
                (model) => {
                    if (!isMounted) return; // Check if component is still mounted

                    let loadedModel;
                    if (model.scene) { //gltf/glb
                        loadedModel = model.scene;
                    } else { //obj
                        loadedModel = model;
                    }

                    // Center the model
                    const boundingBox = new THREE.Box3().setFromObject(loadedModel);
                    const center = boundingBox.getCenter(new THREE.Vector3());
                    loadedModel.position.x -= center.x;
                    loadedModel.position.y -= center.y;
                    loadedModel.position.z -= center.z;

                    scene.add(loadedModel);

                    // Adjust camera to fit model
                    const maxSize = Math.max(
                        boundingBox.max.x - boundingBox.min.x,
                        boundingBox.max.y - boundingBox.min.y,
                        boundingBox.max.z - boundingBox.min.z
                    );
                    const fitHeightDistance = maxSize / (2 * Math.atan(Math.PI * camera.fov / 360));
                    const fitWidthDistance = fitHeightDistance / camera.aspect;
                    const distance = Math.max(fitHeightDistance, fitWidthDistance) * 1.2; // 1.2 for a little extra space
                    controls.target.set(center.x, center.y, center.z);
                    camera.position.set(center.x, center.y, center.z + distance);
                    controls.update();

                    setLoading(false);
                },
                (xhr) => {
                    if (xhr.lengthComputable) {
                        const percentComplete = xhr.loaded / xhr.total * 100;
                        console.log('Model ' + url + ' ' + Math.round(percentComplete, 2) + '% loaded');
                    }
                },
                (err) => {
                    if (!isMounted) return; // Check again in error callback
                    const errorMsg = `Error loading model ${url}: ${err.message}`;
                    console.error(errorMsg, err);
                    setError(errorMsg);
                    setLoading(false);
                }
            );
        };

        // Initial load
        if (modelSrc) {
            loadModel(modelSrc);
        }


        const animate = () => {
            if (!isMounted) return; // Stop animation if unmounted
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        };

        animate();

        const handleResize = () => {
            if (!isMounted) return;
            const newWidth = container.clientWidth;
            const newHeight = container.clientHeight;
            camera.aspect = newWidth / newHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(newWidth, newHeight);
        };

        window.addEventListener('resize', handleResize);

        // Cleanup function
        return () => {
            isMounted = false; // Set flag to prevent further actions
            window.removeEventListener('resize', handleResize);
            if (renderer) {
                renderer.dispose(); // Properly dispose of the renderer
            }
            if (scene) {
                scene.traverse(obj => {
                    if (obj.geometry) obj.geometry.dispose();
                    if (obj.material) {
                        if (obj.material.map) obj.material.dispose();       // Diffuse
                        if (obj.material.specularMap) obj.material.specularMap.dispose(); // Specular
                        if (obj.material.normalMap) obj.material.normalMap.dispose();   // Normal
                        if (obj.material.emissiveMap) obj.material.emissiveMap.dispose(); // Emissive
                        if (obj.material.aoMap) obj.material.aoMap.dispose();       // AO
                        if (Array.isArray(obj.material)) {
                            obj.material.forEach(mat => {
                                if (mat.map) mat.map.dispose();
                                if (mat.specularMap) mat.specularMap.dispose();
                                if (mat.normalMap) mat.normalMap.dispose();
                                if (mat.emissiveMap) mat.emissiveMap.dispose();
                                if (mat.aoMap) mat.aoMap.dispose();
                            });
                        }
                    }
                });
            }
            if (controls) {
                controls.dispose();
            }
            if (container && renderer && renderer.domElement) {
                container.removeChild(renderer.domElement);
            }
        };
    }, [modelSrc,  ]); // removed theme


    return (
        <div
            ref={mountRef}
            className={cn(
                "w-full aspect-square relative",
                "bg-transparent",  // Important:  Make sure the background is transparent
                className
            )}
        >
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <div className="text-white text-lg">Loading Model...</div>
                </div>
            )}
            {error && (
                <div className="absolute inset-0 flex items-center justify-center bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                    <strong className="font-bold">Error: </strong>
                    <span className="block sm:inline">{error}</span>
                </div>
            )}
        </div>
    );
};

jest.mock('three', () => {
  const originalThree = jest.requireActual('three');
  return {
    ...originalThree,
    WebGLRenderer: jest.fn(() => ({
      setSize: jest.fn(),
      render: jest.fn(),
      domElement: { /* Mocked DOM element */ },
    })),
  };
});

describe('ModelViewer', () => {
  it('renders without crashing', () => {
    render(<ModelViewer />);
  });
});

export default ModelViewer;
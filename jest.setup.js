// Mock global document.createElement to support canvas in JSDOM
global.document = global.document || {
    createElement: jest.fn(() => ({
      getContext: jest.fn(),
    })),
  };
  
  // Suppress WebGLRenderer errors in Jest (JSDOM does not support WebGL)
  jest.spyOn(console, 'error').mockImplementation((message) => {
    if (message.includes('THREE.WebGLRenderer: Error creating WebGL context.')) {
      return;
    }
    console.error(message);
  });
  
  // Mock Three.js
  jest.mock('three', () => {
    const originalThree = jest.requireActual('three');
    return {
      ...originalThree,
      WebGLRenderer: jest.fn().mockImplementation(() => ({
        setPixelRatio: jest.fn(),
        setSize: jest.fn(),
        get domElement() {
          return { style: {}, nodeName: 'CANVAS', nodeType: 1 };
        },
        render: jest.fn(),
        dispose: jest.fn(),
      })),
    };
  });
  
  // Mock OrbitControls
  jest.mock('three/examples/jsm/controls/OrbitControls', () => ({
    OrbitControls: jest.fn(() => ({
      update: jest.fn(),
      dispose: jest.fn(),
    })),
  }));
  
  // Ensure React Router warnings are suppressed
  try {
    const { unstable_setFutureFlags } = require('react-router');
    unstable_setFutureFlags({
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    });
  } catch (error) {
    // Fail silently if react-router version does not support unstable_setFutureFlags
  }
  
  // Define global HTMLCanvasElement for tests
  Object.defineProperty(global, 'HTMLCanvasElement', {
    writable: true,
    value: class {
      constructor() {
        this._width = 800;
        this._height = 600;
      }
      getContext() {
        return {
          fillRect: jest.fn(),
          clearRect: jest.fn(),
          getImageData: jest.fn(() => ({ data: new Uint8Array() })),
          putImageData: jest.fn(),
          createImageData: jest.fn(),
          setTransform: jest.fn(),
          drawImage: jest.fn(),
          save: jest.fn(),
          restore: jest.fn(),
          beginPath: jest.fn(),
          moveTo: jest.fn(),
          lineTo: jest.fn(),
          closePath: jest.fn(),
          stroke: jest.fn(),
          translate: jest.fn(),
          scale: jest.fn(),
          rotate: jest.fn(),
          arc: jest.fn(),
          fill: jest.fn(),
        };
      }
      get width() {
        return this._width;
      }
      set width(value) {
        this._width = value;
      }
      get height() {
        return this._height;
      }
      set height(value) {
        this._height = value;
      }
      toDataURL() {
        return '';
      }
      getBoundingClientRect() {
        return { width: this._width, height: this._height, top: 0, left: 0, right: this._width, bottom: this._height };
      }
    },
  });
  
  // Clear mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });  
// Mock canvas API for Jest
class MockWebGLContext {
  createBuffer() { return {}; }
  bindBuffer() {}
  bufferData() {}
  createProgram() { return {}; }
  createShader() { return {}; }
  // Add other WebGL methods as needed
}

class MockCanvas {
  constructor() {
    this.style = {};
    this.addEventListener = jest.fn();
    this.removeEventListener = jest.fn();
    this.appendChild = jest.fn();
    this.removeChild = jest.fn();
    this.getContext = jest.fn((contextType) => {
      if (contextType === 'webgl' || contextType === 'webgl2') {
        return new MockWebGLContext();
      }
      return {};
    });
  }

  get width() { return 800; }
  set width(value) { }
  get height() { return 600; }
  set height(value) { }
}

// Set up global mocks
global.HTMLCanvasElement = MockCanvas;
global.WebGLRenderingContext = MockWebGLContext;
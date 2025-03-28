const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  getProjects: () => ipcRenderer.invoke('get-projects'),
  runOptimization: (params) => ipcRenderer.invoke('run-optimization', params)
});
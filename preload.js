const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  getProjects: async () => {
    try {
      return await ipcRenderer.invoke('get-projects');
    } catch (error) {
      console.error('Error fetching projects:', error);
      throw error;
    }
  },
  runOptimization: async (params) => {
    try {
      return await ipcRenderer.invoke('run-optimization', params);
    } catch (error) {
      console.error('Error running optimization:', error);
      throw error;
    }
  }
});
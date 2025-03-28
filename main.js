const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const sqlite3 = require('sqlite3').verbose();
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let db;

function createWindow() {
  try {
    mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      webPreferences: {
        nodeIntegration: false, // Security: Disable nodeIntegration
        contextIsolation: true, // Security: Enable contextIsolation
        enableRemoteModule: false, // Security: Disable remote module
        webSecurity: true, // Always enable web security
        preload: path.join(__dirname, 'preload.js') // Add preload script
      },
      show: false,
      backgroundColor: '#ffffff'
    });

    if (isDev) {
      mainWindow.loadURL('http://localhost:3000'); // Match with Vite config
      mainWindow.webContents.openDevTools();
    } else {
      mainWindow.loadFile(path.join(__dirname, 'build', 'index.html'));
    }

    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
    });

    mainWindow.on('closed', () => {
      mainWindow = null;
    });
  } catch (error) {
    console.error('Error creating window:', error);
    app.quit();
  }
}

async function initDatabase() {
  try {
    const dbPath = path.join(app.getPath('userData'), 'projects.db');
    db = new sqlite3.Database(dbPath);

    // Promisify database operations
    const runQuery = (query) => new Promise((resolve, reject) => {
      db.run(query, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });

    await runQuery(`
      CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        settings JSON,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Database initialization error:', error);
    throw error;
  }
}

function setupIPC() {

  ipcMain.handle('delete-project', async (event, projectId) => {
    // Add delete logic
  });
  
  ipcMain.handle('get-project', async (event, projectId) => {
    // Add get single project logic
  });
  
  // Projects API
  ipcMain.handle('get-projects', async () => {
    return new Promise((resolve, reject) => {
      db.all('SELECT * FROM projects ORDER BY created_at DESC', [], (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  });

  // Optimization API
  ipcMain.handle('run-optimization', async (event, { inputPath, outputPath }) => {
    if (!inputPath || !outputPath) {
      throw new Error('Invalid input or output path');
    }

    return new Promise((resolve, reject) => {
      const pythonScript = path.join(__dirname, 'src', 'backend', 'main.py');
      const python = spawn('python', [pythonScript, inputPath, outputPath]);

      let stdoutData = '';
      let stderrData = '';

      python.stdout.on('data', (data) => {
        stdoutData += data;
        console.log(`Python output: ${data}`);
      });

      python.stderr.on('data', (data) => {
        stderrData += data;
        console.error(`Python error: ${data}`);
      });

      python.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout: stdoutData });
        } else {
          reject(new Error(`Python script failed: ${stderrData}`));
        }
      });

      python.on('error', (error) => {
        reject(new Error(`Failed to start Python process: ${error.message}`));
      });
    });
  });
}

// App lifecycle
app.whenReady().then(async () => {
  try {
    await initDatabase();
    setupIPC();
    createWindow();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  } catch (error) {
    console.error('Application startup error:', error);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', async () => {
  if (db) {
    await new Promise((resolve) => {
      db.close((err) => {
        if (err) console.error('Error closing database:', err);
        resolve();
      });
    });
  }
});

// Global error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  app.quit();
});

process.on('unhandledRejection', (error) => {
  console.error('Unhandled Rejection:', error);
});
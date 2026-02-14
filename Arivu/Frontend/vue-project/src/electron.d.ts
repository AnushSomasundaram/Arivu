/**
 * TypeScript declarations for Electron API exposed via preload script
 */

export interface ElectronAPI {
  getApiConfig: () => Promise<{ baseUrl: string }>
  onBackendStatus: (callback: (status: { ready: boolean; url?: string; error?: string }) => void) => void
  platform: NodeJS.Platform
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI
  }
}

export {}

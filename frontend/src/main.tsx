import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { FarmerLanguageProvider } from './i18n/FarmerLanguageContext.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <FarmerLanguageProvider>
      <App />
    </FarmerLanguageProvider>
  </StrictMode>,
)

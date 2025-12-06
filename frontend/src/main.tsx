import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Debug: Log to confirm script is loading
console.log('main.tsx is loading...')

const rootElement = document.getElementById('root')
console.log('Root element:', rootElement)

if (!rootElement) {
  document.body.innerHTML = '<h1 style="color: white; padding: 20px;">ERROR: Root element not found!</h1>'
  throw new Error('Root element not found')
}

try {
  console.log('Creating React root...')
  const root = ReactDOM.createRoot(rootElement)
  console.log('Rendering App...')
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
  console.log('App rendered successfully!')
} catch (error) {
  console.error('Error rendering app:', error)
  document.body.innerHTML = `<div style="color: white; padding: 20px;">
    <h1>Error Loading App</h1>
    <pre>${error}</pre>
  </div>`
}

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import Navigation from './components/Navigation'
import ArchitectureDiagram from './components/ArchitectureDiagram'
import ServicesMatrix from './components/ServicesMatrix'
import DataFlows from './components/DataFlows'
import TechStack from './components/TechStack'
import Metrics from './components/Metrics'
import RealTimeMetrics from './components/RealTimeMetrics'
import ServiceDiscovery from './components/ServiceDiscovery'
import Roadmap from './components/Roadmap'
import About from './components/About'
import LoadingScreen from './components/LoadingScreen'
import ParticleBackground from './components/ParticleBackground'

function App() {
  const [activeSection, setActiveSection] = useState('overview')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Симуляция загрузки данных
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return <ArchitectureDiagram />
      case 'services':
        return <ServicesMatrix />
      case 'flows':
        return <DataFlows />
      case 'tech':
        return <TechStack />
      case 'metrics':
        return <RealTimeMetrics />
      case 'legacy-metrics':
        return <Metrics />
      case 'discovery':
        return <ServiceDiscovery />
      case 'roadmap':
        return <Roadmap />
      case 'about':
        return <About />
      default:
        return <ArchitectureDiagram />
    }
  }

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white relative overflow-hidden">
      <ParticleBackground />
      
      <div className="relative z-10">
        <Header />
        <Navigation activeSection={activeSection} setActiveSection={setActiveSection} />
        
        <main className="container mx-auto px-4 py-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </main>

        <footer className="bg-gray-800 border-t border-gray-700 py-8 mt-16">
          <div className="container mx-auto px-4 text-center">
            <p className="text-gray-400">
              © 2025 Open WebUI Hub Architecture. Создано с помощью MiniMax Agent.
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App

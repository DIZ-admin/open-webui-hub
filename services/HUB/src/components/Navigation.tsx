import React from 'react'
import { motion } from 'framer-motion'

interface NavigationProps {
  activeSection: string
  setActiveSection: (section: string) => void
}

const navigationItems = [
  { id: 'overview', name: 'Архитектура', icon: '🏗️' },
  { id: 'services', name: 'Сервисы', icon: '⚙️' },
  { id: 'metrics', name: 'Метрики', icon: '📊' },
  { id: 'discovery', name: 'Discovery', icon: '🔍' },
  { id: 'flows', name: 'Потоки данных', icon: '🔄' },
  { id: 'tech', name: 'Технологии', icon: '💻' },
  { id: 'roadmap', name: 'Roadmap', icon: '🗺️' },
  { id: 'about', name: 'О проекте', icon: 'ℹ️' }
]

const Navigation: React.FC<NavigationProps> = ({ activeSection, setActiveSection }) => {
  return (
    <nav className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-center">
          <div className="flex space-x-1 py-4 overflow-x-auto">
            {navigationItems.map((item, index) => (
              <motion.button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 whitespace-nowrap ${
                  activeSection === item.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <span className="mr-2">{item.icon}</span>
                {item.name}
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navigation

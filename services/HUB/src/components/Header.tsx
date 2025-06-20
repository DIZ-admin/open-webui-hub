import React from 'react'
import { motion } from 'framer-motion'

const Header: React.FC = () => {
  return (
    <motion.header 
      className="bg-gradient-to-r from-blue-900 via-purple-900 to-indigo-900 py-8 border-b border-blue-800/30"
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
    >
      <div className="container mx-auto px-4">
        <div className="text-center">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4">
              Open WebUI Hub
            </h1>
            <div className="text-xl md:text-2xl text-blue-200 mb-2">
              Архитектура микросервисной системы
            </div>
            <div className="text-lg text-gray-300">
              Интерактивная визуализация 13 сервисов и 5 архитектурных слоев
            </div>
          </motion.div>
          
          <motion.div 
            className="mt-6 flex justify-center space-x-4 text-sm text-gray-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full border border-green-500/30">
              ✓ Production Ready
            </span>
            <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full border border-blue-500/30">
              ⚡ High Performance
            </span>
            <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full border border-purple-500/30">
              🔒 Secure
            </span>
          </motion.div>
        </div>
      </div>
    </motion.header>
  )
}

export default Header

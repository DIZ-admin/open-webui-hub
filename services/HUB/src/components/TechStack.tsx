import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface Technology {
  name: string
  version: string
  description: string
  status: 'production' | 'beta' | 'development'
}

interface Category {
  id: string
  name: string
  icon: string
  technologies: Technology[]
}

interface TechStackData {
  categories: Category[]
}

const TechStack: React.FC = () => {
  const [data, setData] = useState<TechStackData | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetch('/data/tech-stack.json')
      .then(res => res.json())
      .then(setData)
  }, [])

  if (!data) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'production':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'beta':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'development':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const filteredCategories = data.categories.map(category => ({
    ...category,
    technologies: category.technologies.filter(tech =>
      tech.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tech.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(category => category.technologies.length > 0)

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
          Технологический стек
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto">
          Полный обзор технологий, используемых в Open WebUI Hub. 
          От инфраструктуры до AI/ML решений - все компоненты современного микросервисного приложения.
        </p>
      </motion.div>

      {/* Поиск */}
      <motion.div
        className="max-w-md mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Поиск технологий..."
          className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
        />
      </motion.div>

      {/* Статистика */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        {[
          {
            title: 'Всего технологий',
            value: data.categories.reduce((acc, cat) => acc + cat.technologies.length, 0),
            color: 'text-blue-400'
          },
          {
            title: 'Production',
            value: data.categories.reduce((acc, cat) => 
              acc + cat.technologies.filter(t => t.status === 'production').length, 0),
            color: 'text-green-400'
          },
          {
            title: 'Beta/Testing',
            value: data.categories.reduce((acc, cat) => 
              acc + cat.technologies.filter(t => t.status === 'beta').length, 0),
            color: 'text-yellow-400'
          },
          {
            title: 'Категорий',
            value: data.categories.length,
            color: 'text-purple-400'
          }
        ].map((stat, index) => (
          <div key={stat.title} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
            <div className="text-sm text-gray-400">{stat.title}</div>
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </motion.div>

      {/* Категории технологий */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {filteredCategories.map((category, categoryIndex) => (
          <motion.div
            key={category.id}
            className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: categoryIndex * 0.1 }}
          >
            <div className="p-6 border-b border-gray-700">
              <h3 className="text-xl font-bold text-white flex items-center">
                <span className="text-2xl mr-3">{category.icon}</span>
                {category.name}
              </h3>
            </div>
            
            <div className="p-6 space-y-4">
              {category.technologies.map((tech, techIndex) => (
                <motion.div
                  key={tech.name}
                  className="bg-gray-700/50 p-4 rounded-lg border border-gray-600 hover:border-gray-500 transition-all duration-200"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: (categoryIndex * 0.1) + (techIndex * 0.05) }}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-white">{tech.name}</h4>
                      <p className="text-sm text-gray-400">Версия: {tech.version}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(tech.status)}`}>
                      {tech.status === 'production' ? 'Production' : 
                       tech.status === 'beta' ? 'Beta' : 'Development'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">{tech.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Архитектурная диаграмма стека */}
      <motion.div
        className="bg-gray-800/50 p-8 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-xl font-bold text-white mb-6 text-center">
          Архитектурные слои технологий
        </h3>
        
        <div className="space-y-4">
          {[
            {
              layer: 'Frontend',
              technologies: ['HTML/CSS/JS', 'React', 'Tailwind CSS'],
              color: 'from-blue-500 to-purple-500'
            },
            {
              layer: 'Backend Services',
              technologies: ['Python', 'FastAPI', 'Flask'],
              color: 'from-green-500 to-blue-500'
            },
            {
              layer: 'AI/ML Layer',
              technologies: ['Ollama', 'LiteLLM', 'Docling', 'EdgeTTS'],
              color: 'from-purple-500 to-pink-500'
            },
            {
              layer: 'Data Layer',
              technologies: ['PostgreSQL', 'pgvector', 'Redis'],
              color: 'from-yellow-500 to-orange-500'
            },
            {
              layer: 'Infrastructure',
              technologies: ['Docker', 'Nginx', 'Cloudflare'],
              color: 'from-gray-500 to-gray-700'
            }
          ].map((layer, index) => (
            <motion.div
              key={layer.layer}
              className="relative"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + (index * 0.1) }}
            >
              <div className={`bg-gradient-to-r ${layer.color} p-4 rounded-lg text-white`}>
                <h4 className="font-bold mb-2">{layer.layer}</h4>
                <div className="flex flex-wrap gap-2">
                  {layer.technologies.map((tech) => (
                    <span
                      key={tech}
                      className="bg-white/20 px-2 py-1 rounded text-sm backdrop-blur-sm"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
              
              {index < 4 && (
                <div className="flex justify-center my-2">
                  <div className="w-0.5 h-4 bg-gray-500"></div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Версионность и совместимость */}
      <motion.div
        className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 p-6 rounded-xl border border-indigo-700/30"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h3 className="text-lg font-bold text-white mb-4">📋 Политика версионирования</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-semibold text-indigo-400 mb-2">Production Ready</h4>
            <p className="text-gray-300">Стабильные версии, готовые для промышленного использования</p>
          </div>
          <div>
            <h4 className="font-semibold text-yellow-400 mb-2">Beta/Testing</h4>
            <p className="text-gray-300">Версии в стадии тестирования, могут содержать ошибки</p>
          </div>
          <div>
            <h4 className="font-semibold text-blue-400 mb-2">Development</h4>
            <p className="text-gray-300">Экспериментальные версии для разработки</p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default TechStack

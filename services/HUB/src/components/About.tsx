import React from 'react'
import { motion } from 'framer-motion'

const About: React.FC = () => {
  const teamMembers = [
    {
      role: 'Архитектор системы',
      name: 'MiniMax Agent',
      description: 'Разработка и визуализация архитектуры',
      avatar: '🤖'
    },
    {
      role: 'DevOps Engineer',
      name: 'Infrastructure Team',
      description: 'Контейнеризация и развертывание',
      avatar: '⚙️'
    },
    {
      role: 'AI/ML Engineer',
      name: 'AI Team',
      description: 'Интеграция AI моделей и RAG',
      avatar: '🧠'
    },
    {
      role: 'Backend Developer',
      name: 'Backend Team',
      description: 'Микросервисы и API',
      avatar: '💻'
    }
  ]

  const technologies = [
    { name: 'React 18', category: 'Frontend' },
    { name: 'TypeScript', category: 'Language' },
    { name: 'Tailwind CSS', category: 'Styling' },
    { name: 'Framer Motion', category: 'Animation' },
    { name: 'Recharts', category: 'Visualization' },
    { name: 'Vite', category: 'Build Tool' }
  ]

  const features = [
    {
      icon: '🏗️',
      title: 'Интерактивная архитектура',
      description: 'Визуализация 5 слоев архитектуры с 13 микросервисами'
    },
    {
      icon: '📊',
      title: 'Метрики в реальном времени',
      description: 'Отслеживание производительности и надежности системы'
    },
    {
      icon: '🔄',
      title: 'Потоки данных',
      description: 'Анимированная визуализация прохождения данных через систему'
    },
    {
      icon: '🗺️',
      title: 'Roadmap развития',
      description: 'Планы развития проекта на ближайшие годы'
    },
    {
      icon: '💻',
      title: 'Технологический стек',
      description: 'Подробная информация о всех используемых технологиях'
    },
    {
      icon: '🎨',
      title: 'Современный дизайн',
      description: 'Адаптивный темный UI с анимациями и эффектами'
    }
  ]

  return (
    <div className="space-y-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          О проекте Open WebUI Hub
        </h2>
        <p className="text-gray-300 max-w-4xl mx-auto text-lg">
          Интерактивная веб-платформа для визуализации и управления архитектурой 
          микросервисной системы Open WebUI Hub - современного решения для работы с AI моделями.
        </p>
      </motion.div>

      {/* Описание проекта */}
      <motion.div
        className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 p-8 rounded-xl border border-blue-700/30"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-2xl font-bold text-white mb-6 text-center">🚀 Миссия проекта</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h4 className="text-lg font-semibold text-blue-400 mb-3">Цели проекта</h4>
            <ul className="space-y-2 text-gray-300">
              <li>• Предоставить интуитивно понятную визуализацию сложной архитектуры</li>
              <li>• Обеспечить прозрачность в работе микросервисов</li>
              <li>• Упростить мониторинг и отладку системы</li>
              <li>• Создать образовательный ресурс для команды разработки</li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold text-purple-400 mb-3">Ключевые принципы</h4>
            <ul className="space-y-2 text-gray-300">
              <li>• Интерактивность и отзывчивость интерфейса</li>
              <li>• Реальные данные и актуальная информация</li>
              <li>• Современные веб-технологии и подходы</li>
              <li>• Адаптивный дизайн для всех устройств</li>
            </ul>
          </div>
        </div>
      </motion.div>

      {/* Функциональность */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="text-2xl font-bold text-white mb-8 text-center">✨ Основная функциональность</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 hover:border-gray-600 transition-all duration-200"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h4 className="text-lg font-semibold text-white mb-2">{feature.title}</h4>
              <p className="text-gray-300 text-sm">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Команда */}
      <motion.div
        className="bg-gray-800/50 p-8 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-2xl font-bold text-white mb-8 text-center">👥 Команда проекта</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {teamMembers.map((member, index) => (
            <motion.div
              key={member.name}
              className="text-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 + index * 0.1 }}
            >
              <div className="text-4xl mb-4">{member.avatar}</div>
              <h4 className="font-semibold text-white mb-1">{member.role}</h4>
              <p className="text-blue-400 mb-2">{member.name}</p>
              <p className="text-sm text-gray-400">{member.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Технологии */}
      <motion.div
        className="bg-gradient-to-br from-green-900/20 to-blue-900/20 p-8 rounded-xl border border-green-700/30"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <h3 className="text-2xl font-bold text-white mb-8 text-center">🛠️ Технологии веб-интерфейса</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {technologies.map((tech, index) => (
            <motion.div
              key={tech.name}
              className="bg-gray-700/50 p-4 rounded-lg text-center border border-gray-600"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 + index * 0.05 }}
              whileHover={{ scale: 1.05 }}
            >
              <div className="font-semibold text-white text-sm mb-1">{tech.name}</div>
              <div className="text-xs text-gray-400">{tech.category}</div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Архитектура Open WebUI Hub */}
      <motion.div
        className="bg-gray-800/50 p-8 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h3 className="text-2xl font-bold text-white mb-6 text-center">🏗️ Архитектура Open WebUI Hub</h3>
        
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="text-lg font-semibold text-blue-400 mb-4">Микросервисная архитектура</h4>
              <p className="text-gray-300 mb-4">
                Open WebUI Hub построен по принципам микросервисной архитектуры, что обеспечивает:
              </p>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Независимое развертывание и масштабирование сервисов</li>
                <li>• Высокую отказоустойчивость системы</li>
                <li>• Гибкость в выборе технологий для каждого сервиса</li>
                <li>• Простоту поддержки и обновления</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-green-400 mb-4">AI-первый подход</h4>
              <p className="text-gray-300 mb-4">
                Система спроектирована с фокусом на работу с AI моделями:
              </p>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>• Локальные LLM модели через Ollama</li>
                <li>• RAG (Retrieval-Augmented Generation) pipeline</li>
                <li>• Векторный поиск с pgvector</li>
                <li>• Обработка документов и TTS синтез</li>
              </ul>
            </div>
          </div>

          <div className="bg-gray-700/30 p-6 rounded-lg">
            <h4 className="text-lg font-semibold text-purple-400 mb-4">🔧 Ключевые компоненты системы</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <h5 className="font-semibold text-white mb-2">Презентационный слой</h5>
                <p className="text-gray-300">Open WebUI для взаимодействия с пользователем, Nginx как reverse proxy</p>
              </div>
              <div>
                <h5 className="font-semibold text-white mb-2">Сервисный слой</h5>
                <p className="text-gray-300">AI сервисы (Ollama, EdgeTTS), обработка документов (Docling, Tika)</p>
              </div>
              <div>
                <h5 className="font-semibold text-white mb-2">Данные и инфраструктура</h5>
                <p className="text-gray-300">PostgreSQL с pgvector, Redis для кэширования, Docker для контейнеризации</p>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Контакты и ссылки */}
      <motion.div
        className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 p-8 rounded-xl border border-purple-700/30 text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <h3 className="text-2xl font-bold text-white mb-4">📞 Контакты и ресурсы</h3>
        <p className="text-gray-300 mb-6">
          Интерактивная архитектура создана для демонстрации возможностей современных веб-технологий 
          в визуализации сложных систем.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
          <div>
            <h4 className="font-semibold text-purple-400 mb-2">📚 Документация</h4>
            <p className="text-gray-300">Техническая документация и API reference</p>
          </div>
          <div>
            <h4 className="font-semibold text-pink-400 mb-2">🐛 Баг-трекер</h4>
            <p className="text-gray-300">Сообщения об ошибках и предложения улучшений</p>
          </div>
          <div>
            <h4 className="font-semibold text-blue-400 mb-2">💬 Сообщество</h4>
            <p className="text-gray-300">Обсуждения и поддержка пользователей</p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-700">
          <p className="text-gray-400 text-sm">
            © 2025 Open WebUI Hub Architecture Visualization. 
            Создано с использованием современных веб-технологий и лучших практик UX/UI дизайна.
          </p>
        </div>
      </motion.div>
    </div>
  )
}

export default About

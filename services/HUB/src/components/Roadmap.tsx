import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface RoadmapItem {
  title: string
  description: string
  status: 'completed' | 'in-progress' | 'planned' | 'research'
  priority: 'high' | 'medium' | 'low'
  assignee: string
}

interface Phase {
  id: string
  name: string
  timeframe: string
  color: string
  progress: number
  items: RoadmapItem[]
}

interface Milestone {
  date: string
  title: string
  description: string
}

interface RoadmapData {
  phases: Phase[]
  milestones: Milestone[]
}

const Roadmap: React.FC = () => {
  const [data, setData] = useState<RoadmapData | null>(null)
  const [selectedPhase, setSelectedPhase] = useState<string | null>(null)

  useEffect(() => {
    fetch('/data/roadmap.json')
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
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'in-progress':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'planned':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'research':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-400'
      case 'medium':
        return 'text-yellow-400'
      case 'low':
        return 'text-green-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅'
      case 'in-progress':
        return '🔄'
      case 'planned':
        return '📋'
      case 'research':
        return '🔬'
      default:
        return '❓'
    }
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">
          Roadmap развития
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto">
          Стратегический план развития Open WebUI Hub на ближайшие годы. 
          От краткосрочных улучшений до долгосрочных архитектурных изменений.
        </p>
      </motion.div>

      {/* Общий прогресс */}
      <motion.div
        className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-xl font-bold text-white mb-4">Общий прогресс проекта</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.phases.map((phase, index) => (
            <div key={phase.id} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-300">{phase.name}</span>
                <span className="text-sm text-gray-400">{phase.progress}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3">
                <motion.div
                  className="h-3 rounded-full"
                  style={{ backgroundColor: phase.color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${phase.progress}%` }}
                  transition={{ delay: 0.3 + index * 0.1, duration: 1 }}
                />
              </div>
              <div className="text-xs text-gray-500">{phase.timeframe}</div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Фазы развития */}
      <div className="space-y-6">
        {data.phases.map((phase, phaseIndex) => (
          <motion.div
            key={phase.id}
            className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + phaseIndex * 0.1 }}
          >
            <div 
              className="p-6 cursor-pointer"
              style={{ 
                background: `linear-gradient(135deg, ${phase.color}20 0%, transparent 50%)`,
                borderLeft: `4px solid ${phase.color}`
              }}
              onClick={() => setSelectedPhase(selectedPhase === phase.id ? null : phase.id)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white flex items-center">
                    <div 
                      className="w-4 h-4 rounded mr-3"
                      style={{ backgroundColor: phase.color }}
                    />
                    {phase.name}
                  </h3>
                  <p className="text-gray-300 mt-1">{phase.timeframe}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold" style={{ color: phase.color }}>
                    {phase.progress}%
                  </div>
                  <div className="text-sm text-gray-400">
                    {selectedPhase === phase.id ? '▼' : '▶'}
                  </div>
                </div>
              </div>
            </div>

            {selectedPhase === phase.id && (
              <motion.div
                className="border-t border-gray-700"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <div className="p-6 space-y-4">
                  {phase.items.map((item, itemIndex) => (
                    <motion.div
                      key={item.title}
                      className="bg-gray-700/50 p-4 rounded-lg border border-gray-600"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: itemIndex * 0.1 }}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h4 className="font-semibold text-white flex items-center">
                            <span className="mr-2">{getStatusIcon(item.status)}</span>
                            {item.title}
                          </h4>
                          <p className="text-sm text-gray-300 mt-1">{item.description}</p>
                        </div>
                        <div className="ml-4 flex flex-col items-end space-y-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(item.status)}`}>
                            {item.status}
                          </span>
                          <span className={`text-xs font-medium ${getPriorityColor(item.priority)}`}>
                            {item.priority} priority
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Исполнитель: {item.assignee}</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Timeline милестоунов */}
      <motion.div
        className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <h3 className="text-xl font-bold text-white mb-6">🎯 Ключевые милестоуны</h3>
        <div className="relative">
          {/* Временная линия */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500 via-purple-500 to-pink-500"></div>
          
          <div className="space-y-8">
            {data.milestones.map((milestone, index) => (
              <motion.div
                key={milestone.date}
                className="relative flex items-start"
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.1 }}
              >
                <div className="absolute left-6 w-4 h-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full border-2 border-gray-900"></div>
                <div className="ml-16 bg-gray-700/50 p-4 rounded-lg border border-gray-600 flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-white">{milestone.title}</h4>
                    <span className="text-sm text-gray-400">{milestone.date}</span>
                  </div>
                  <p className="text-sm text-gray-300">{milestone.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Статистика */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        {[
          {
            title: 'Всего задач',
            value: data.phases.reduce((acc, phase) => acc + phase.items.length, 0),
            color: 'text-blue-400'
          },
          {
            title: 'Завершено',
            value: data.phases.reduce((acc, phase) => 
              acc + phase.items.filter(item => item.status === 'completed').length, 0),
            color: 'text-green-400'
          },
          {
            title: 'В работе',
            value: data.phases.reduce((acc, phase) => 
              acc + phase.items.filter(item => item.status === 'in-progress').length, 0),
            color: 'text-yellow-400'
          },
          {
            title: 'Запланировано',
            value: data.phases.reduce((acc, phase) => 
              acc + phase.items.filter(item => item.status === 'planned' || item.status === 'research').length, 0),
            color: 'text-purple-400'
          }
        ].map((stat, index) => (
          <div key={stat.title} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
            <div className="text-sm text-gray-400">{stat.title}</div>
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </motion.div>

      {/* Примечания */}
      <motion.div
        className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 p-6 rounded-xl border border-indigo-700/30"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
      >
        <h3 className="text-lg font-bold text-white mb-4">📝 Примечания к roadmap</h3>
        <div className="space-y-2 text-sm text-gray-300">
          <div>• Временные рамки являются приблизительными и могут изменяться в зависимости от приоритетов</div>
          <div>• Статус "Research" означает проведение исследований и анализа технической осуществимости</div>
          <div>• Высокоприоритетные задачи могут быть перенесены в более ранние фазы</div>
          <div>• Прогресс обновляется еженедельно на основе отчетов команд разработки</div>
        </div>
      </motion.div>
    </div>
  )
}

export default Roadmap

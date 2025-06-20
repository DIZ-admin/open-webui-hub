import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Service, Layer, ArchitectureData } from '../types'

const ArchitectureDiagram: React.FC = () => {
  const [data, setData] = useState<ArchitectureData | null>(null)
  const [selectedService, setSelectedService] = useState<Service | null>(null)
  const [hoveredLayer, setHoveredLayer] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchData = async () => {
    setIsLoading(true)
    try {
      // Fetch data from backend API instead of static JSON
      const response = await fetch('/api/architecture')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const newData = await response.json()
      setData(newData)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error fetching architecture data:', error)
      // Fallback to static data if API is not available
      try {
        const fallbackResponse = await fetch('/data/services.json')
        const fallbackData = await fallbackResponse.json()
        setData(fallbackData)
        setLastUpdate(new Date())
      } catch (fallbackError) {
        console.error('Error fetching fallback data:', fallbackError)
      }
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchData()
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh])

  if (!data) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  const getServicesByLayer = (layerId: string) => {
    const layer = data.layers.find(l => l.id === layerId)
    if (!layer) return []
    
    return data.services.filter(service => layer.services.includes(service.id))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Production Ready':
        return 'bg-green-500'
      case 'NEW Feature':
        return 'bg-blue-500'
      case 'Needs Improvement':
        return 'bg-yellow-500'
      case 'Needs Health Check':
        return 'bg-orange-500'
      case 'Needs Attention':
        return 'bg-red-500'
      case 'Operational':
        return 'bg-purple-500'
      case 'Error':
        return 'bg-red-600'
      default:
        return 'bg-gray-500'
    }
  }

  const getHealthStatusColor = (healthStatus: string, containerStatus: string) => {
    if (healthStatus === 'healthy' && containerStatus === 'running') {
      return 'bg-green-500'
    } else if (healthStatus === 'unhealthy' || containerStatus === 'exited') {
      return 'bg-red-500'
    } else if (healthStatus === 'unreachable' || containerStatus === 'not_found') {
      return 'bg-orange-500'
    } else {
      return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Архитектура системы Open WebUI Hub
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto mb-4">
          Интерактивная диаграмма показывает 5 архитектурных слоев с {data?.total_services || 13} микросервисами.
          Наведите курсор на слой или кликните на сервис для получения детальной информации.
        </p>

        {/* Control Panel */}
        <div className="flex items-center justify-center space-x-4 mb-4">
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            <span>{isLoading ? '🔄' : '🔄'}</span>
            <span>{isLoading ? 'Обновление...' : 'Обновить'}</span>
          </button>

          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
              autoRefresh
                ? 'bg-green-600 hover:bg-green-700 text-white'
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            }`}
          >
            <span>{autoRefresh ? '⏸️' : '▶️'}</span>
            <span>Авто-обновление</span>
          </button>

          {lastUpdate && (
            <span className="text-sm text-gray-400">
              Обновлено: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>

        {/* Status Summary */}
        {data && (
          <div className="flex items-center justify-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-300">Здоровых: {data.healthy_services || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-gray-300">Запущенных: {data.running_containers || 0}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              <span className="text-gray-300">Всего: {data.total_services || 0}</span>
            </div>
          </div>
        )}
      </motion.div>

      <div className="grid gap-4">
        {data.layers.map((layer, index) => (
          <motion.div
            key={layer.id}
            className={`relative p-6 rounded-xl border-2 transition-all duration-300 ${
              hoveredLayer === layer.id
                ? 'border-white/50 bg-gray-800/80'
                : 'border-gray-700/50 bg-gray-800/40'
            }`}
            style={{
              backgroundColor: hoveredLayer === layer.id ? layer.color + '20' : undefined
            }}
            onMouseEnter={() => setHoveredLayer(layer.id)}
            onMouseLeave={() => setHoveredLayer(null)}
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="mb-4">
              <h3 className="text-xl font-bold text-white mb-2 flex items-center">
                <div 
                  className="w-4 h-4 rounded mr-3"
                  style={{ backgroundColor: layer.color }}
                />
                {layer.name}
              </h3>
              <p className="text-gray-300 text-sm">{layer.description}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {getServicesByLayer(layer.id).map((service) => (
                <motion.div
                  key={service.id}
                  className="bg-gray-700/50 p-4 rounded-lg border border-gray-600 cursor-pointer hover:bg-gray-600/50 transition-all duration-200"
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setSelectedService(service)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-white text-sm">{service.name}</h4>
                    <div className="flex space-x-1">
                      <div
                        className={`w-2 h-2 rounded-full ${getHealthStatusColor(service.health_status, service.container_status)}`}
                        title={`Health: ${service.health_status || 'unknown'}, Container: ${service.container_status || 'unknown'}`}
                      />
                      <div className={`w-2 h-2 rounded-full ${getStatusColor(service.status)}`} />
                    </div>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs text-gray-300">{service.category}</p>
                    {service.port && (
                      <p className="text-xs text-blue-400">:{service.port}</p>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 line-clamp-2">{service.description}</p>
                  {service.error && (
                    <p className="text-xs text-red-400 mt-1">Error: {service.error}</p>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Модальное окно с информацией о сервисе */}
      {selectedService && (
        <motion.div
          className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSelectedService(null)}
        >
          <motion.div
            className="bg-gray-800 p-6 rounded-xl max-w-md w-full border border-gray-600"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-white">{selectedService.name}</h3>
              <button
                onClick={() => setSelectedService(null)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-400">Категория:</span>
                <span className="ml-2 text-white">{selectedService.category}</span>
              </div>
              <div>
                <span className="text-sm text-gray-400">Статус:</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs ${getStatusColor(selectedService.status)} text-white`}>
                  {selectedService.status}
                </span>
              </div>
              {selectedService.port && (
                <div>
                  <span className="text-sm text-gray-400">Порт:</span>
                  <span className="ml-2 text-blue-400">{selectedService.port}</span>
                </div>
              )}
              <div>
                <span className="text-sm text-gray-400">Контейнер:</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs ${
                  selectedService.container_status === 'running' ? 'bg-green-600' :
                  selectedService.container_status === 'exited' ? 'bg-red-600' : 'bg-gray-600'
                } text-white`}>
                  {selectedService.container_status || 'unknown'}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-400">Здоровье:</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs ${
                  selectedService.health_status === 'healthy' ? 'bg-green-600' :
                  selectedService.health_status === 'unhealthy' ? 'bg-red-600' :
                  selectedService.health_status === 'unreachable' ? 'bg-orange-600' : 'bg-gray-600'
                } text-white`}>
                  {selectedService.health_status || 'unknown'}
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-400">Описание:</span>
                <p className="mt-1 text-white">{selectedService.description}</p>
              </div>
              {selectedService.error && (
                <div>
                  <span className="text-sm text-gray-400">Ошибка:</span>
                  <p className="mt-1 text-red-400 text-sm">{selectedService.error}</p>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Легенда статусов */}
      <motion.div
        className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-lg font-bold text-white mb-4">Легенда статусов</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {[
            { status: 'Production Ready', count: data.services.filter(s => s.status === 'Production Ready').length },
            { status: 'NEW Feature', count: data.services.filter(s => s.status === 'NEW Feature').length },
            { status: 'Needs Improvement', count: data.services.filter(s => s.status === 'Needs Improvement').length },
            { status: 'Needs Health Check', count: data.services.filter(s => s.status === 'Needs Health Check').length },
            { status: 'Operational', count: data.services.filter(s => s.status === 'Operational').length },
          ].map((item) => (
            <div key={item.status} className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(item.status)}`} />
              <span className="text-sm text-gray-300">{item.status}</span>
              <span className="text-xs text-gray-500">({item.count})</span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default ArchitectureDiagram

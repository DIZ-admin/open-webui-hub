import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { DiscoveredService, DiscoveryData } from '../types'

const ServiceDiscovery: React.FC = () => {
  const [data, setData] = useState<DiscoveryData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDiscoveryData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/discovery')
      if (response.status === 403) {
        setError('Service Discovery отключен в конфигурации')
        return
      }
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const newData = await response.json()
      setData(newData)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error fetching discovery data:', error)
      setError(error instanceof Error ? error.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDiscoveryData()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchDiscoveryData()
    }, 15000) // Refresh every 15 seconds

    return () => clearInterval(interval)
  }, [autoRefresh])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
        return 'bg-green-500'
      case 'exited':
        return 'bg-red-500'
      case 'paused':
        return 'bg-yellow-500'
      case 'restarting':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  const formatPorts = (ports: any) => {
    if (!ports || typeof ports !== 'object') return 'N/A'
    
    const portStrings = Object.entries(ports).map(([containerPort, hostPorts]) => {
      if (Array.isArray(hostPorts) && hostPorts.length > 0) {
        const hostPort = hostPorts[0].HostPort
        return `${hostPort}:${containerPort}`
      }
      return containerPort
    })
    
    return portStrings.join(', ') || 'N/A'
  }

  const isConfiguredService = (serviceName: string) => {
    return data?.configured_services.includes(serviceName) || false
  }

  if (error) {
    return (
      <div className="space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
            Service Discovery
          </h2>
          <div className="bg-red-900/50 border border-red-600 p-6 rounded-xl max-w-2xl mx-auto">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">⚠️</div>
              <div>
                <h3 className="text-red-400 font-semibold">Service Discovery недоступен</h3>
                <p className="text-red-300 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  const discoveredServices = Object.entries(data.discovered_services)
  const configuredCount = discoveredServices.filter(([name]) => isConfiguredService(name)).length
  const unconfiguredCount = discoveredServices.length - configuredCount

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
          Service Discovery
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto mb-4">
          Автоматическое обнаружение Docker контейнеров в экосистеме Open WebUI Hub.
        </p>
        
        {/* Control Panel */}
        <div className="flex items-center justify-center space-x-4 mb-4">
          <button
            onClick={fetchDiscoveryData}
            disabled={isLoading}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            <span>{isLoading ? '🔄' : '🔍'}</span>
            <span>{isLoading ? 'Сканирование...' : 'Сканировать'}</span>
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
            <span>Авто-сканирование (15с)</span>
          </button>
          
          {lastUpdate && (
            <span className="text-sm text-gray-400">
              Обновлено: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>

        {/* Summary */}
        <div className="flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-300">Настроенных: {configuredCount}</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-gray-300">Обнаруженных: {unconfiguredCount}</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-gray-300">Всего: {discoveredServices.length}</span>
          </div>
        </div>
      </motion.div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {discoveredServices.map(([serviceName, service], index) => (
          <motion.div
            key={serviceName}
            className={`p-6 rounded-xl border-2 transition-all duration-300 ${
              isConfiguredService(serviceName)
                ? 'border-green-500/50 bg-green-900/20'
                : 'border-yellow-500/50 bg-yellow-900/20'
            }`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-white">{serviceName}</h3>
                <p className="text-sm text-gray-400">{service.container_name}</p>
              </div>
              <div className="flex items-center space-x-2">
                {isConfiguredService(serviceName) && (
                  <div className="w-3 h-3 bg-green-500 rounded-full" title="Настроенный сервис" />
                )}
                <div 
                  className={`w-3 h-3 rounded-full ${getStatusColor(service.status)}`}
                  title={`Status: ${service.status}`}
                />
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-400">Статус:</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs ${getStatusColor(service.status)} text-white`}>
                  {service.status}
                </span>
              </div>
              
              <div>
                <span className="text-sm text-gray-400">Образ:</span>
                <p className="text-white text-sm mt-1 break-all">{service.image}</p>
              </div>
              
              <div>
                <span className="text-sm text-gray-400">Порты:</span>
                <p className="text-blue-400 text-sm mt-1">{formatPorts(service.ports)}</p>
              </div>

              {Object.keys(service.labels).length > 0 && (
                <div>
                  <span className="text-sm text-gray-400">Метки:</span>
                  <div className="mt-1 max-h-20 overflow-y-auto">
                    {Object.entries(service.labels).slice(0, 3).map(([key, value]) => (
                      <div key={key} className="text-xs text-gray-300 truncate">
                        <span className="text-gray-500">{key}:</span> {value as string}
                      </div>
                    ))}
                    {Object.keys(service.labels).length > 3 && (
                      <div className="text-xs text-gray-500">
                        +{Object.keys(service.labels).length - 3} больше...
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {!isConfiguredService(serviceName) && (
              <div className="mt-4 p-3 bg-yellow-900/30 border border-yellow-600/50 rounded-lg">
                <p className="text-yellow-400 text-xs">
                  ⚠️ Сервис обнаружен, но не настроен в Hub конфигурации
                </p>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {discoveredServices.length === 0 && (
        <motion.div
          className="text-center py-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-300 mb-2">
            Сервисы не обнаружены
          </h3>
          <p className="text-gray-400">
            Проверьте, что Docker контейнеры запущены и доступны для сканирования.
          </p>
        </motion.div>
      )}

      {/* Configuration Info */}
      <motion.div
        className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-lg font-bold text-white mb-4">Настроенные сервисы</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
          {data.configured_services.map((serviceName) => (
            <div
              key={serviceName}
              className="px-3 py-1 bg-green-600/20 border border-green-600/50 rounded text-green-400 text-sm text-center"
            >
              {serviceName}
            </div>
          ))}
        </div>
        <p className="text-gray-400 text-sm mt-3">
          Эти сервисы настроены в Hub конфигурации и отслеживаются системой мониторинга.
        </p>
      </motion.div>
    </div>
  )
}

export default ServiceDiscovery

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { MetricsData } from '../types'

const RealTimeMetrics: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchMetrics = async () => {
    setIsLoading(true)
    try {
      // Получаем данные из Hub Service API через Nginx
      const response = await fetch('/api/metrics')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setMetrics(data)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error fetching metrics:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchMetrics()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchMetrics()
    }, 10000) // Refresh every 10 seconds for metrics

    return () => clearInterval(interval)
  }, [autoRefresh])

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    return `${hours}ч ${minutes}м ${secs}с`
  }

  const getHealthPercentage = (healthy: number, total: number) => {
    return total > 0 ? Math.round((healthy / total) * 100) : 0
  }

  if (!metrics) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
          Метрики системы в реальном времени
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto mb-4">
          Мониторинг состояния всех сервисов и контейнеров Open WebUI Hub в режиме реального времени.
        </p>
        
        {/* Control Panel */}
        <div className="flex items-center justify-center space-x-4 mb-4">
          <button
            onClick={fetchMetrics}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            <span>{isLoading ? '🔄' : '📊'}</span>
            <span>{isLoading ? 'Обновление...' : 'Обновить метрики'}</span>
          </button>
          
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
              autoRefresh 
                ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            }`}
          >
            <span>{autoRefresh ? '⏸️' : '▶️'}</span>
            <span>Авто-обновление (10с)</span>
          </button>
          
          {lastUpdate && (
            <span className="text-sm text-gray-400">
              Обновлено: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </motion.div>

      {/* Main Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          className="bg-gradient-to-br from-green-600 to-green-700 p-6 rounded-xl text-white"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Здоровых сервисов</p>
              <p className="text-3xl font-bold">{metrics.healthy_services}</p>
              <p className="text-green-100 text-sm">из {metrics.total_services}</p>
            </div>
            <div className="text-4xl">💚</div>
          </div>
          <div className="mt-4">
            <div className="bg-green-800 rounded-full h-2">
              <div 
                className="bg-green-300 h-2 rounded-full transition-all duration-500"
                style={{ width: `${getHealthPercentage(metrics.healthy_services, metrics.total_services)}%` }}
              />
            </div>
            <p className="text-green-100 text-xs mt-1">
              {getHealthPercentage(metrics.healthy_services, metrics.total_services)}% здоровых
            </p>
          </div>
        </motion.div>

        <motion.div
          className="bg-gradient-to-br from-blue-600 to-blue-700 p-6 rounded-xl text-white"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Запущенных контейнеров</p>
              <p className="text-3xl font-bold">{metrics.running_containers}</p>
              <p className="text-blue-100 text-sm">из {metrics.total_services}</p>
            </div>
            <div className="text-4xl">🐳</div>
          </div>
          <div className="mt-4">
            <div className="bg-blue-800 rounded-full h-2">
              <div 
                className="bg-blue-300 h-2 rounded-full transition-all duration-500"
                style={{ width: `${getHealthPercentage(metrics.running_containers, metrics.total_services)}%` }}
              />
            </div>
            <p className="text-blue-100 text-xs mt-1">
              {getHealthPercentage(metrics.running_containers, metrics.total_services)}% запущено
            </p>
          </div>
        </motion.div>

        <motion.div
          className="bg-gradient-to-br from-purple-600 to-purple-700 p-6 rounded-xl text-white"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Архитектурных слоев</p>
              <p className="text-3xl font-bold">{metrics.layers}</p>
              <p className="text-purple-100 text-sm">уровней</p>
            </div>
            <div className="text-4xl">🏗️</div>
          </div>
        </motion.div>

        <motion.div
          className="bg-gradient-to-br from-orange-600 to-orange-700 p-6 rounded-xl text-white"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Время работы</p>
              <p className="text-lg font-bold">{formatUptime(metrics.uptime)}</p>
              <p className="text-orange-100 text-sm">Hub API</p>
            </div>
            <div className="text-4xl">⏱️</div>
          </div>
        </motion.div>
      </div>

      {/* Layer Breakdown */}
      <motion.div
        className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-xl font-bold text-white mb-6">Метрики по слоям архитектуры</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(metrics.layer_metrics).map(([layerId, layerMetrics]) => (
            <div key={layerId} className="bg-gray-700/50 p-4 rounded-lg">
              <h4 className="font-semibold text-white mb-3 capitalize">{layerId} Layer</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">Всего:</span>
                  <span className="text-white">{layerMetrics.total}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">Здоровых:</span>
                  <span className="text-green-400">{layerMetrics.healthy}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">Запущенных:</span>
                  <span className="text-blue-400">{layerMetrics.running}</span>
                </div>
                <div className="mt-2">
                  <div className="bg-gray-600 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${getHealthPercentage(layerMetrics.healthy, layerMetrics.total)}%` }}
                    />
                  </div>
                  <p className="text-gray-400 text-xs mt-1">
                    {getHealthPercentage(layerMetrics.healthy, layerMetrics.total)}% здоровых
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Error Services Alert */}
      {metrics.error_services > 0 && (
        <motion.div
          className="bg-red-900/50 border border-red-600 p-4 rounded-xl"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <div className="flex items-center space-x-3">
            <div className="text-2xl">⚠️</div>
            <div>
              <h4 className="text-red-400 font-semibold">Внимание: Обнаружены проблемы</h4>
              <p className="text-red-300 text-sm">
                {metrics.error_services} сервис(ов) имеют ошибки. Проверьте детали в диаграмме архитектуры.
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default RealTimeMetrics

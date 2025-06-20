import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

interface MetricHistory {
  time: string
  value: number
}

interface Metric {
  current: number
  target: number
  unit: string
  trend: 'improving' | 'stable' | 'declining'
  history?: MetricHistory[]
}

interface ServiceResource {
  name: string
  cpu: number
  memory: number
  disk: number
  network: number
}

interface MetricsData {
  performance: {
    responseTime: Metric
    throughput: Metric
    errorRate: Metric
  }
  reliability: {
    uptime: Metric
    mttr: Metric
    mtbf: Metric
  }
  resources: {
    services: ServiceResource[]
  }
}

const Metrics: React.FC = () => {
  const [data, setData] = useState<MetricsData | null>(null)
  const [activeTab, setActiveTab] = useState<'performance' | 'reliability' | 'resources'>('performance')

  useEffect(() => {
    fetch('/data/metrics.json')
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

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return '📈'
      case 'stable':
        return '➡️'
      case 'declining':
        return '📉'
      default:
        return '➡️'
    }
  }

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'improving':
        return 'text-green-400'
      case 'stable':
        return 'text-blue-400'
      case 'declining':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusColor = (current: number, target: number, higherIsBetter: boolean) => {
    const isGood = higherIsBetter ? current >= target : current <= target
    return isGood ? 'text-green-400' : 'text-yellow-400'
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

  const resourceDistribution = data.resources.services.map(service => ({
    name: service.name,
    cpu: service.cpu,
    memory: (service.memory / 4096) * 100,
    disk: service.disk,
    network: service.network
  }))

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
          Метрики производительности
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto">
          Реальные показатели производительности, надежности и использования ресурсов системы Open WebUI Hub.
          Мониторинг критически важных метрик для обеспечения стабильной работы.
        </p>
      </motion.div>

      {/* Навигация по вкладкам */}
      <motion.div
        className="flex justify-center space-x-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {[
          { id: 'performance', name: 'Производительность', icon: '⚡' },
          { id: 'reliability', name: 'Надежность', icon: '🛡️' },
          { id: 'resources', name: 'Ресурсы', icon: '📊' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </motion.div>

      {/* Производительность */}
      {activeTab === 'performance' && (
        <motion.div
          key="performance"
          className="space-y-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          {/* Основные метрики */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Время отклика',
                metric: data.performance.responseTime,
                higherIsBetter: false
              },
              {
                title: 'Пропускная способность',
                metric: data.performance.throughput,
                higherIsBetter: true
              },
              {
                title: 'Процент ошибок',
                metric: data.performance.errorRate,
                higherIsBetter: false
              }
            ].map((item, index) => (
              <motion.div
                key={item.title}
                className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                  <span className={getTrendColor(item.metric.trend)}>
                    {getTrendIcon(item.metric.trend)}
                  </span>
                </div>
                
                <div className="mb-4">
                  <div className={`text-3xl font-bold ${getStatusColor(item.metric.current, item.metric.target, item.higherIsBetter)}`}>
                    {item.metric.current}{item.metric.unit}
                  </div>
                  <div className="text-sm text-gray-400">
                    Цель: {item.metric.target}{item.metric.unit}
                  </div>
                </div>

                {item.metric.history && (
                  <div className="h-24">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={item.metric.history}>
                        <Line 
                          type="monotone" 
                          dataKey="value" 
                          stroke="#3B82F6" 
                          strokeWidth={2} 
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* Подробный график времени отклика */}
          <motion.div
            className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <h3 className="text-xl font-bold text-white mb-4">Время отклика за последние 24 часа</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.performance.responseTime.history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="time" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3B82F6" 
                    strokeWidth={3}
                    dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Надежность */}
      {activeTab === 'reliability' && (
        <motion.div
          key="reliability"
          className="space-y-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Uptime',
                metric: data.reliability.uptime,
                higherIsBetter: true,
                description: 'Время безотказной работы'
              },
              {
                title: 'MTTR',
                metric: data.reliability.mttr,
                higherIsBetter: false,
                description: 'Среднее время восстановления'
              },
              {
                title: 'MTBF',
                metric: data.reliability.mtbf,
                higherIsBetter: true,
                description: 'Среднее время между отказами'
              }
            ].map((item, index) => (
              <motion.div
                key={item.title}
                className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-white">{item.title}</h3>
                  <span className={getTrendColor(item.metric.trend)}>
                    {getTrendIcon(item.metric.trend)}
                  </span>
                </div>
                
                <p className="text-sm text-gray-400 mb-4">{item.description}</p>
                
                <div className="mb-4">
                  <div className={`text-3xl font-bold ${getStatusColor(item.metric.current, item.metric.target, item.higherIsBetter)}`}>
                    {item.metric.current}{item.metric.unit}
                  </div>
                  <div className="text-sm text-gray-400">
                    Цель: {item.metric.target}{item.metric.unit}
                  </div>
                </div>

                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      getStatusColor(item.metric.current, item.metric.target, item.higherIsBetter) === 'text-green-400' 
                        ? 'bg-green-500' 
                        : 'bg-yellow-500'
                    }`}
                    style={{ 
                      width: `${Math.min(100, (item.metric.current / item.metric.target) * 100)}%` 
                    }}
                  />
                </div>
              </motion.div>
            ))}
          </div>

          {/* SLA Dashboard */}
          <motion.div
            className="bg-gradient-to-br from-green-900/30 to-blue-900/30 p-6 rounded-xl border border-green-700/30"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <h3 className="text-xl font-bold text-white mb-4">📋 SLA Соглашения</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Доступность сервиса</span>
                  <span className="text-green-400 font-bold">99.95%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Максимальное время отклика</span>
                  <span className="text-blue-400 font-bold">500ms</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Максимальный процент ошибок</span>
                  <span className="text-yellow-400 font-bold">1%</span>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Время восстановления</span>
                  <span className="text-purple-400 font-bold">&lt; 15 min</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Уведомления о проблемах</span>
                  <span className="text-orange-400 font-bold">&lt; 2 min</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Плановые работы</span>
                  <span className="text-indigo-400 font-bold">&lt; 4ч/месяц</span>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* Ресурсы */}
      {activeTab === 'resources' && (
        <motion.div
          key="resources"
          className="space-y-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          {/* Общее использование ресурсов */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div
              className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h3 className="text-xl font-bold text-white mb-4">CPU использование по сервисам</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={resourceDistribution.slice(0, 8)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#9CA3AF" angle={-45} textAnchor="end" height={80} />
                    <YAxis stroke="#9CA3AF" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #374151',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="cpu" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            <motion.div
              className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h3 className="text-xl font-bold text-white mb-4">Распределение памяти</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={resourceDistribution.slice(0, 6)}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="memory"
                    >
                      {resourceDistribution.slice(0, 6).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </motion.div>
          </div>

          {/* Детальная таблица ресурсов */}
          <motion.div
            className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="p-6 border-b border-gray-700">
              <h3 className="text-xl font-bold text-white">Детальное использование ресурсов</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Сервис</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">CPU %</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Memory %</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Disk I/O %</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Network %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {data.resources.services.map((service, index) => (
                    <motion.tr
                      key={service.name}
                      className="hover:bg-gray-700/30 transition-colors"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.05 }}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                        {service.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-700 rounded-full h-2 mr-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${service.cpu}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-300">{service.cpu}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-700 rounded-full h-2 mr-2">
                            <div
                              className="bg-green-500 h-2 rounded-full"
                              style={{ width: `${service.memory}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-300">{service.memory}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-700 rounded-full h-2 mr-2">
                            <div
                              className="bg-yellow-500 h-2 rounded-full"
                              style={{ width: `${service.disk}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-300">{service.disk}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-700 rounded-full h-2 mr-2">
                            <div
                              className="bg-purple-500 h-2 rounded-full"
                              style={{ width: `${service.network}%` }}
                            />
                          </div>
                          <span className="text-sm text-gray-300">{service.network}%</span>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  )
}

export default Metrics

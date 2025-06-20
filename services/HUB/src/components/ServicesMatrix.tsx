import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface Service {
  id: string
  name: string
  category: string
  ports: string
  status: string
  layer: string
  description: string
  healthCheck: boolean
  version: string
  cpu: number
  memory: number
}

const ServicesMatrix: React.FC = () => {
  const [services, setServices] = useState<Service[]>([])
  const [filteredServices, setFilteredServices] = useState<Service[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [sortBy, setSortBy] = useState<keyof Service>('name')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')

  useEffect(() => {
    fetch('/data/services.json')
      .then(res => res.json())
      .then(data => {
        setServices(data.services)
        setFilteredServices(data.services)
      })
  }, [])

  useEffect(() => {
    let filtered = services.filter(service => {
      const matchesSearch = service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           service.description.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'all' || service.status === statusFilter
      const matchesCategory = categoryFilter === 'all' || service.category === categoryFilter
      
      return matchesSearch && matchesStatus && matchesCategory
    })

    // Сортировка
    filtered.sort((a, b) => {
      const aValue = a[sortBy]
      const bValue = b[sortBy]
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue
      }
      
      return 0
    })

    setFilteredServices(filtered)
  }, [services, searchTerm, statusFilter, categoryFilter, sortBy, sortDirection])

  const handleSort = (column: keyof Service) => {
    if (sortBy === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortDirection('asc')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Production Ready':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'NEW Feature':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'Needs Improvement':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'Needs Health Check':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
      case 'Operational':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const uniqueStatuses = [...new Set(services.map(s => s.status))]
  const uniqueCategories = [...new Set(services.map(s => s.category))]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
          Матрица сервисов
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto">
          Интерактивная таблица всех 13 микросервисов с возможностью фильтрации, поиска и сортировки.
          Отслеживайте статус, ресурсы и конфигурацию каждого сервиса.
        </p>
      </motion.div>

      {/* Панель фильтров */}
      <motion.div
        className="bg-gray-800/50 p-6 rounded-xl border border-gray-700"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Поиск</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Поиск по названию или описанию..."
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Статус</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="all">Все статусы</option>
              {uniqueStatuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Категория</label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="all">Все категории</option>
              {uniqueCategories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('all')
                setCategoryFilter('all')
              }}
              className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
            >
              Сбросить фильтры
            </button>
          </div>
        </div>
        
        <div className="mt-4 text-sm text-gray-400">
          Найдено сервисов: {filteredServices.length} из {services.length}
        </div>
      </motion.div>

      {/* Таблица сервисов */}
      <motion.div
        className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700/50">
              <tr>
                {[
                  { key: 'name', label: 'Сервис' },
                  { key: 'category', label: 'Категория' },
                  { key: 'ports', label: 'Порты' },
                  { key: 'status', label: 'Статус' },
                  { key: 'version', label: 'Версия' },
                  { key: 'cpu', label: 'CPU %' },
                  { key: 'memory', label: 'Memory MB' },
                  { key: 'healthCheck', label: 'Health Check' }
                ].map((column) => (
                  <th
                    key={column.key}
                    onClick={() => handleSort(column.key as keyof Service)}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-600/50 transition-colors"
                  >
                    <div className="flex items-center space-x-1">
                      <span>{column.label}</span>
                      {sortBy === column.key && (
                        <span className="text-blue-400">
                          {sortDirection === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredServices.map((service, index) => (
                <motion.tr
                  key={service.id}
                  className="hover:bg-gray-700/30 transition-colors"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-white">{service.name}</div>
                      <div className="text-sm text-gray-400 max-w-xs truncate">{service.description}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium bg-gray-700 text-gray-300 rounded">
                      {service.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {service.ports}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded border ${getStatusColor(service.status)}`}>
                      {service.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                    {service.version}
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
                          style={{ width: `${Math.min(100, (service.memory / 4096) * 100)}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-300">{service.memory}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      service.healthCheck
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {service.healthCheck ? '✓ Активен' : '✗ Отключен'}
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Статистика */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        {[
          { 
            title: 'Всего сервисов', 
            value: services.length,
            color: 'text-blue-400'
          },
          { 
            title: 'Production Ready', 
            value: services.filter(s => s.status === 'Production Ready').length,
            color: 'text-green-400'
          },
          { 
            title: 'Активные Health Checks', 
            value: services.filter(s => s.healthCheck).length,
            color: 'text-purple-400'
          },
          { 
            title: 'Среднее CPU', 
            value: Math.round(services.reduce((acc, s) => acc + s.cpu, 0) / services.length) + '%',
            color: 'text-orange-400'
          }
        ].map((stat, index) => (
          <div key={stat.title} className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
            <div className="text-sm text-gray-400">{stat.title}</div>
            <div className={`text-2xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </motion.div>
    </div>
  )
}

export default ServicesMatrix

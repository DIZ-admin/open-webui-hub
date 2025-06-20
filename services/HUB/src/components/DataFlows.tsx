import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface FlowStep {
  id: string
  name: string
  description: string
  position: { x: number; y: number }
}

interface FlowConnection {
  from: string
  to: string
}

interface DataFlow {
  id: string
  name: string
  description: string
  color: string
  steps: FlowStep[]
  connections: FlowConnection[]
}

interface FlowData {
  flows: DataFlow[]
}

const DataFlows: React.FC = () => {
  const [data, setData] = useState<FlowData | null>(null)
  const [activeFlow, setActiveFlow] = useState<string>('user-flow')
  const [animatingStep, setAnimatingStep] = useState<number>(-1)
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    fetch('/data/data-flows.json')
      .then(res => res.json())
      .then(setData)
  }, [])

  const startAnimation = (flowId: string) => {
    const flow = data?.flows.find(f => f.id === flowId)
    if (!flow || isAnimating) return

    setIsAnimating(true)
    setAnimatingStep(0)

    let stepIndex = 0
    const animate = () => {
      if (stepIndex < flow.steps.length) {
        setAnimatingStep(stepIndex)
        stepIndex++
        setTimeout(animate, 800)
      } else {
        setIsAnimating(false)
        setAnimatingStep(-1)
      }
    }

    animate()
  }

  if (!data) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  const currentFlow = data.flows.find(f => f.id === activeFlow)

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Потоки данных
        </h2>
        <p className="text-gray-300 max-w-3xl mx-auto">
          Визуализация основных потоков данных в системе Open WebUI Hub. 
          Проследите путь от пользовательского запроса до ответа AI модели.
        </p>
      </motion.div>

      {/* Селектор потоков */}
      <motion.div
        className="flex justify-center space-x-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {data.flows.map((flow) => (
          <button
            key={flow.id}
            onClick={() => setActiveFlow(flow.id)}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeFlow === flow.id
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {flow.name}
          </button>
        ))}
      </motion.div>

      {currentFlow && (
        <motion.div
          key={currentFlow.id}
          className="space-y-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          {/* Описание потока */}
          <div className="bg-gray-800/50 p-6 rounded-xl border border-gray-700 text-center">
            <h3 className="text-xl font-bold text-white mb-2">{currentFlow.name}</h3>
            <p className="text-gray-300">{currentFlow.description}</p>
            <button
              onClick={() => startAnimation(currentFlow.id)}
              disabled={isAnimating}
              className={`mt-4 px-6 py-2 rounded-lg font-medium transition-all ${
                isAnimating
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:shadow-lg'
              }`}
            >
              {isAnimating ? 'Анимация...' : 'Запустить анимацию'}
            </button>
          </div>

          {/* Диаграмма потока */}
          <div className="bg-gray-800/30 p-8 rounded-xl border border-gray-700 overflow-x-auto">
            <div className="relative min-w-max" style={{ height: '300px' }}>
              <svg
                className="absolute inset-0 w-full h-full pointer-events-none"
                style={{ zIndex: 1 }}
              >
                {/* Рисуем соединения */}
                {currentFlow.connections.map((connection, index) => {
                  const fromStep = currentFlow.steps.find(s => s.id === connection.from)
                  const toStep = currentFlow.steps.find(s => s.id === connection.to)
                  
                  if (!fromStep || !toStep) return null

                  const shouldAnimate = animatingStep >= currentFlow.steps.findIndex(s => s.id === connection.from) &&
                                       animatingStep >= currentFlow.steps.findIndex(s => s.id === connection.to)

                  return (
                    <motion.line
                      key={`${connection.from}-${connection.to}`}
                      x1={fromStep.position.x + 80}
                      y1={fromStep.position.y + 25}
                      x2={toStep.position.x}
                      y2={toStep.position.y + 25}
                      stroke={shouldAnimate ? currentFlow.color : '#374151'}
                      strokeWidth="2"
                      strokeDasharray="5,5"
                      className="transition-all duration-300"
                    >
                      {shouldAnimate && (
                        <animate
                          attributeName="stroke-dashoffset"
                          values="10;0"
                          dur="1s"
                          repeatCount="indefinite"
                        />
                      )}
                    </motion.line>
                  )
                })}

                {/* Стрелки */}
                {currentFlow.connections.map((connection) => {
                  const fromStep = currentFlow.steps.find(s => s.id === connection.from)
                  const toStep = currentFlow.steps.find(s => s.id === connection.to)
                  
                  if (!fromStep || !toStep) return null

                  const shouldAnimate = animatingStep >= currentFlow.steps.findIndex(s => s.id === connection.from) &&
                                       animatingStep >= currentFlow.steps.findIndex(s => s.id === connection.to)

                  return (
                    <polygon
                      key={`arrow-${connection.from}-${connection.to}`}
                      points={`${toStep.position.x - 8},${toStep.position.y + 15} ${toStep.position.x - 8},${toStep.position.y + 35} ${toStep.position.x},${toStep.position.y + 25}`}
                      fill={shouldAnimate ? currentFlow.color : '#374151'}
                      className="transition-all duration-300"
                    />
                  )
                })}
              </svg>

              {/* Шаги потока */}
              {currentFlow.steps.map((step, index) => {
                const isActive = animatingStep >= index
                const isCurrent = animatingStep === index

                return (
                  <motion.div
                    key={step.id}
                    className={`absolute w-40 p-4 rounded-lg border-2 transition-all duration-300 ${
                      isActive
                        ? 'bg-gray-700 border-blue-500 shadow-lg'
                        : 'bg-gray-800 border-gray-600'
                    } ${isCurrent ? 'ring-4 ring-blue-400/50' : ''}`}
                    style={{
                      left: `${step.position.x}px`,
                      top: `${step.position.y}px`,
                      zIndex: 10
                    }}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className="text-center">
                      <div className={`text-sm font-medium mb-2 ${isActive ? 'text-white' : 'text-gray-400'}`}>
                        {step.name}
                      </div>
                      <div className={`text-xs ${isActive ? 'text-gray-300' : 'text-gray-500'}`}>
                        {step.description}
                      </div>
                      {isCurrent && (
                        <motion.div
                          className="absolute -top-2 -right-2 w-4 h-4 bg-blue-500 rounded-full"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ repeat: Infinity, duration: 1 }}
                        />
                      )}
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>

          {/* Детали шагов */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            {currentFlow.steps.map((step, index) => (
              <motion.div
                key={step.id}
                className={`bg-gray-800/50 p-4 rounded-lg border transition-all duration-300 ${
                  animatingStep >= index
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-700'
                }`}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-center mb-2">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3 ${
                    animatingStep >= index
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-600 text-gray-300'
                  }`}>
                    {index + 1}
                  </div>
                  <h4 className="font-semibold text-white">{step.name}</h4>
                </div>
                <p className="text-sm text-gray-300">{step.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      )}

      {/* Информационные карточки */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 p-6 rounded-xl border border-blue-700/30">
          <h3 className="text-lg font-bold text-white mb-3">🚀 Производительность потоков</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-300">Средняя задержка:</span>
              <span className="text-blue-400 font-medium">380ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">Пропускная способность:</span>
              <span className="text-green-400 font-medium">1,250 req/sec</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">Процент ошибок:</span>
              <span className="text-yellow-400 font-medium">0.3%</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-900/30 to-blue-900/30 p-6 rounded-xl border border-green-700/30">
          <h3 className="text-lg font-bold text-white mb-3">🔧 Оптимизации</h3>
          <div className="space-y-2 text-sm text-gray-300">
            <div>• Кэширование результатов в Redis</div>
            <div>• Асинхронная обработка документов</div>
            <div>• Батчевая векторизация текста</div>
            <div>• Connection pooling для БД</div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default DataFlows

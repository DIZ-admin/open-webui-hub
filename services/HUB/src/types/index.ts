export interface Service {
  id: string
  name: string
  category: string
  status: string
  description: string
  layer?: string
  port?: number
  container_status?: string
  health_status?: string
  error?: string
}

export interface Layer {
  id: string
  name: string
  description: string
  color: string
  services: string[]
}

export interface ArchitectureData {
  services: Service[]
  layers: Layer[]
  timestamp: number
  total_services: number
  healthy_services: number
  running_containers: number
}

export interface MetricsData {
  total_services: number
  healthy_services: number
  running_containers: number
  error_services: number
  layers: number
  uptime: number
  timestamp: number
  layer_metrics: {
    [key: string]: {
      total: number
      healthy: number
      running: number
    }
  }
}

export interface DiscoveredService {
  container_name: string
  status: string
  image: string
  ports: any
  labels: any
}

export interface DiscoveryData {
  discovered_services: { [key: string]: DiscoveredService }
  configured_services: string[]
  timestamp: number
}

import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

export function formatPercentage(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100)
}

export function formatDuration(ms?: number) {
  if (!ms) return '0ms'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

export function getAgentColor(agent: string) {
  const map: Record<string, string> = {
    customer_agent: 'text-blue-400',
    crm_agent: 'text-purple-400',
    policy_agent: 'text-emerald-400',
    fraud_agent: 'text-amber-400',
    decision_agent: 'text-rose-400',
  }
  return map[agent] || 'text-gray-400'
}

export function getAgentBgColor(agent: string) {
  const map: Record<string, string> = {
    customer_agent: 'bg-blue-50 border-blue-200',
    crm_agent:      'bg-purple-50 border-purple-200',
    policy_agent:   'bg-emerald-50 border-emerald-200',
    fraud_agent:    'bg-amber-50 border-amber-200',
    decision_agent: 'bg-indigo-50 border-indigo-200',
  }
  return map[agent] || 'bg-gray-50 border-gray-200'
}

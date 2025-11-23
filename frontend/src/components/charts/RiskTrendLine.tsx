import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import type { SnapshotHistory } from '../../types'

interface RiskTrendLineProps {
  data: SnapshotHistory[]
}

export default function RiskTrendLine({ data }: RiskTrendLineProps) {
  const chartData = data.map((item) => {
    const date = new Date(item.created_at)
    return {
      name: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      fullDate: date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
      overspending: Math.round(item.overspending_prob * 100),
      stress: Math.round(item.financial_stress_prob * 100),
    }
  })

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            domain={[0, 100]}
            tickFormatter={(value) => `${value}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
            labelFormatter={(label: string, payload: any[]) => {
              if (payload && payload[0]) {
                return payload[0].payload.fullDate
              }
              return label
            }}
            formatter={(value: number, name: string) => [
              `${value}%`,
              name === 'overspending' ? 'Overspending Risk' : 'Financial Stress'
            ]}
          />
          <Legend
            verticalAlign="top"
            height={36}
            formatter={(value) => (
              <span className="text-sm text-gray-600">
                {value === 'overspending' ? 'Overspending Risk' : 'Financial Stress'}
              </span>
            )}
          />
          <Line
            type="monotone"
            dataKey="overspending"
            stroke="#f97316"
            strokeWidth={2}
            dot={{ fill: '#f97316', strokeWidth: 2 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="stress"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={{ fill: '#8b5cf6', strokeWidth: 2 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

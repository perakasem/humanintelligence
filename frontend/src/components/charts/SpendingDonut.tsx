import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import type { SpendingBreakdown } from '../../types'

interface SpendingDonutProps {
  data: SpendingBreakdown
}

// Muted earth-tone palette
const COLORS = [
  '#a3785d', // warm brown
  '#7a8561', // sage green
  '#c4a882', // sand
  '#8b7355', // taupe
  '#b5967a', // camel
  '#6b7c6e', // muted green
  '#d4b896', // wheat
  '#9c8b7a', // stone
  '#a89f91', // greige
  '#c9baa8', // linen
]

const LABELS: Record<string, string> = {
  tuition: 'Tuition',
  housing: 'Housing',
  food: 'Food',
  transportation: 'Transport',
  books_supplies: 'Books',
  entertainment: 'Entertainment',
  personal_care: 'Personal',
  technology: 'Tech',
  health_wellness: 'Health',
  miscellaneous: 'Misc',
}

export default function SpendingDonut({ data }: SpendingDonutProps) {
  const chartData = Object.entries(data)
    .filter(([_, value]) => value > 0)
    .map(([key, value]) => ({
      name: LABELS[key] || key,
      value,
    }))
    .sort((a, b) => b.value - a.value)

  return (
    <div className="h-96">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="40%"
            innerRadius={50}
            outerRadius={85}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => [`$${value}`, '']}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend
            verticalAlign="bottom"
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => <span className="text-xs text-stone-600">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

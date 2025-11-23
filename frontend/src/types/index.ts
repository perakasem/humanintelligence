// User types
export interface User {
  id: string
  email: string
  name?: string
  picture?: string
}

// Auth types
export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
  is_new_user: boolean
}

// Intake types
export interface RawAnswer {
  question_id: string
  answer: string
}

export interface IntakeRequest {
  raw_answers: RawAnswer[]
}

export interface SummaryOutput {
  summary_paragraph: string
  key_points: string[]
}

export interface Analytics {
  total_resources: number
  total_spending: number
  net_balance: number
  is_overspending: boolean
  overspending_amount: number
  savings_potential: number
  food_share: number
  housing_share: number
  entertainment_share: number
  discretionary_share: number
  tuition_share: number
}

export interface IntakeResponse {
  snapshot_id: string
  overspending_prob: number
  financial_stress_prob: number
  summary: SummaryOutput
  analytics: Analytics
  created_at: string
}

// Dashboard types
export interface SpendingBreakdown {
  tuition: number
  housing: number
  food: number
  transportation: number
  books_supplies: number
  entertainment: number
  personal_care: number
  technology: number
  health_wellness: number
  miscellaneous: number
}

export interface SnapshotHistory {
  snapshot_id: string
  created_at: string
  overspending_prob: number
  financial_stress_prob: number
  total_spending: number
  total_resources: number
}

export interface RiskScores {
  overspending_prob: number
  financial_stress_prob: number
}

export interface DashboardResponse {
  user_id: string
  latest_snapshot_id?: string
  spending_breakdown?: SpendingBreakdown
  analytics?: Analytics
  risk_scores?: RiskScores
  summary?: SummaryOutput
  history: SnapshotHistory[]
  has_data: boolean
}

// Teacher types
export interface LessonOutline {
  title: string
  bullet_points: string[]
}

export interface FieldUpdate {
  field: string
  value: number
}

export interface TeacherOutput {
  response_type?: 'coaching' | 'feedback' | 'update'
  priority_issues: string[]
  explanation: string
  actions_for_week: string[]
  lesson_outline?: LessonOutline | null
  field_updates?: FieldUpdate[]
}

export interface TeacherChatRequest {
  snapshot_id?: string
  user_message: string
}

export interface TeacherChatResponse {
  interaction_id: string
  teacher_output: TeacherOutput
  created_at: string
}

export interface ChatHistory {
  interaction_id: string
  user_message: string
  teacher_response: TeacherOutput
  created_at: string
}

// Enum mappings
export const GENDER_OPTIONS = [
  { value: '0', label: 'Male' },
  { value: '1', label: 'Female' },
  { value: '2', label: 'Non-binary' },
  { value: '3', label: 'Prefer not to say' },
]

export const YEAR_OPTIONS = [
  { value: '0', label: 'Freshman' },
  { value: '1', label: 'Sophomore' },
  { value: '2', label: 'Junior' },
  { value: '3', label: 'Senior' },
  { value: '4', label: 'Graduate' },
]

export const MAJOR_OPTIONS = [
  { value: '0', label: 'STEM' },
  { value: '1', label: 'Business' },
  { value: '2', label: 'Humanities' },
  { value: '3', label: 'Social Sciences' },
  { value: '4', label: 'Arts' },
  { value: '5', label: 'Health Sciences' },
  { value: '6', label: 'Education' },
  { value: '7', label: 'Law' },
  { value: '8', label: 'Other' },
]

export const PAYMENT_OPTIONS = [
  { value: '0', label: 'Cash' },
  { value: '1', label: 'Credit Card' },
  { value: '2', label: 'Debit Card' },
  { value: '3', label: 'Mobile Payment' },
]

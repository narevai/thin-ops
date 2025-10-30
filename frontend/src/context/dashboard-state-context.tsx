import { createContext, useContext, useEffect, useState } from 'react'
import { config } from '@/lib/api'
import { OverviewFilters as OverviewFiltersType } from '@/features/dashboard/components/tabs/types'

type DashboardStateProviderProps = {
  children: React.ReactNode
  storageKey?: string
}

type DashboardState = {
  filters: OverviewFiltersType
  setFilters: (filters: OverviewFiltersType) => void
  isInitialized: boolean
}

const createDefaultDateRange = () => {
  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(endDate.getDate() - 30)

  return {
    start_date: startDate.toISOString(),
    end_date: endDate.toISOString(),
  }
}

const createDemoDateRange = () => {
  return {
    start_date: new Date('2024-07-20T00:00:00.000Z').toISOString(),
    end_date: new Date('2025-07-20T00:00:00.000Z').toISOString(),
  }
}

const getInitialFilters = (): OverviewFiltersType => {
  return {
    dateRange: createDefaultDateRange(),
    providers: [],
    services: [],
  }
}

const initialState: DashboardState = {
  filters: getInitialFilters(),
  setFilters: () => null,
  isInitialized: false,
}

const DashboardStateContext = createContext<DashboardState>(initialState)

export function DashboardStateProvider({
  children,
  storageKey = 'dashboard-state',
  ...props
}: DashboardStateProviderProps) {
  const [filters, setFiltersState] =
    useState<OverviewFiltersType>(getInitialFilters)
  const [isInitialized, setIsInitialized] = useState<boolean>(false)

  // Initialize filters based on demo mode if user hasn't modified them before
  useEffect(() => {
    const initializeFilters = async () => {
      const hasStoredFilters = localStorage.getItem(storageKey)

      // If user has stored filters, use them and mark as initialized
      if (hasStoredFilters) {
        setIsInitialized(true)
        return
      }

      // Otherwise, check demo mode and set appropriate defaults
      try {
        const { data } = await config.get()
        const demo = data?.settings.demo

        setFiltersState({
          dateRange: demo ? createDemoDateRange() : createDefaultDateRange(),
          providers: [],
          services: [],
        })
      } catch {
        // If config fetch fails, just use default date range
        setFiltersState({
          dateRange: createDefaultDateRange(),
          providers: [],
          services: [],
        })
      }

      setIsInitialized(true)
    }

    initializeFilters()
  }, [storageKey])

  const setFilters = (newFilters: OverviewFiltersType) => {
    setFiltersState(newFilters)
    localStorage.setItem(storageKey, JSON.stringify(newFilters))
  }

  const value = {
    filters,
    setFilters,
    isInitialized,
  }

  return (
    <DashboardStateContext.Provider {...props} value={value}>
      {children}
    </DashboardStateContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useDashboardState = () => {
  const context = useContext(DashboardStateContext)

  if (context === undefined)
    throw new Error(
      'useDashboardState must be used within a DashboardStateProvider'
    )

  return context
}

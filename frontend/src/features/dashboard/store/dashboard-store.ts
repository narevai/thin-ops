import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { DateRange } from '../components/filters/types'
import { OverviewFilters } from '../components/tabs/types'

interface DashboardState {
  // Filters
  filters: OverviewFilters

  // Demo mode
  isDemo: boolean

  // Actions
  setDateRange: (dateRange: DateRange) => void
  setProviders: (providers: string[]) => void
  setServices: (services: string[]) => void
  setFilters: (filters: OverviewFilters) => void
  setIsDemo: (isDemo: boolean) => void
  resetFilters: () => void
}

// Default date range for demo mode
const DEFAULT_DEMO_DATE_RANGE: DateRange = {
  start_date: new Date('2024-07-20T00:00:00.000Z').toISOString(),
  end_date: new Date('2025-07-20T00:00:00.000Z').toISOString(),
}

const DEFAULT_FILTERS: OverviewFilters = {
  dateRange: DEFAULT_DEMO_DATE_RANGE,
  providers: [],
  services: [],
}

export const useDashboardStore = create<DashboardState>()(
  persist(
    (set) => ({
      filters: DEFAULT_FILTERS,
      isDemo: false,

      setDateRange: (dateRange: DateRange) => {
        // Always update the state, persistence is handled by the persist middleware
        set((state) => ({
          filters: { ...state.filters, dateRange },
        }))
      },

      setProviders: (providers: string[]) => {
        set((state) => ({
          filters: { ...state.filters, providers },
        }))
      },

      setServices: (services: string[]) => {
        set((state) => ({
          filters: { ...state.filters, services },
        }))
      },

      setFilters: (filters: OverviewFilters) => {
        // Always update filters, persistence is handled by the persist middleware
        set({ filters })
      },

      setIsDemo: (isDemo: boolean) => {
        // When switching to demo mode, reset date range to default
        if (isDemo) {
          set((state) => ({
            isDemo,
            filters: {
              ...state.filters,
              dateRange: DEFAULT_DEMO_DATE_RANGE,
            },
          }))
        } else {
          set({ isDemo })
        }
      },

      resetFilters: () => {
        set({ filters: DEFAULT_FILTERS })
      },
    }),
    {
      name: 'dashboard-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist filters if not in demo mode
      partialize: (state) => {
        // In demo mode, don't persist any filters
        if (state.isDemo) {
          return {}
        }
        // Otherwise persist all filters
        return { filters: state.filters }
      },
    }
  )
)

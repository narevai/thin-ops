import {
  IconAdjustmentsHorizontal,
  IconSortAscendingLetters,
  IconSortDescendingLetters,
} from '@tabler/icons-react'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const appText = new Map<string, string>([
  ['all', 'All Apps'],
  ['connected', 'Connected'],
  ['notConnected', 'Not Connected'],
])

interface AppsFiltersProps {
  searchTerm: string
  appType: 'all' | 'connected' | 'notConnected'
  sort: 'ascending' | 'descending'
  onSearchChange: (value: string) => void
  onAppTypeChange: (value: 'all' | 'connected' | 'notConnected') => void
  onSortChange: (value: 'ascending' | 'descending') => void
}

export function AppsFilters({
  searchTerm,
  appType,
  sort,
  onSearchChange,
  onAppTypeChange,
  onSortChange,
}: AppsFiltersProps) {
  return (
    <div className='my-4 flex items-end justify-between sm:my-0 sm:items-center'>
      <div className='flex flex-col gap-4 sm:my-4 sm:flex-row'>
        <Input
          placeholder='Filter providers...'
          className='h-9 w-40 lg:w-[250px]'
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        <Select value={appType} onValueChange={onAppTypeChange}>
          <SelectTrigger className='w-36'>
            <SelectValue>{appText.get(appType)}</SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='all'>All Providers</SelectItem>
            <SelectItem value='connected'>Connected</SelectItem>
            <SelectItem value='notConnected'>Not Connected</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Select value={sort} onValueChange={onSortChange}>
        <SelectTrigger className='w-16'>
          <SelectValue>
            <IconAdjustmentsHorizontal size={18} />
          </SelectValue>
        </SelectTrigger>
        <SelectContent align='end'>
          <SelectItem value='ascending'>
            <div className='flex items-center gap-4'>
              <IconSortAscendingLetters size={16} />
              <span>Ascending</span>
            </div>
          </SelectItem>
          <SelectItem value='descending'>
            <div className='flex items-center gap-4'>
              <IconSortDescendingLetters size={16} />
              <span>Descending</span>
            </div>
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}

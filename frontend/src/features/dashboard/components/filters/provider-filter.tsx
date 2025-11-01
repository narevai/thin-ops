import { useEffect, useState } from 'react'
import { Check, ChevronsUpDown } from 'lucide-react'
import { providers as providersApi } from '@/lib/api'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'

interface ProviderInstance {
  id: string
  name: string
  provider_type: string
  display_name?: string | null
  is_active: boolean
}

interface ProviderFilterProps {
  value: string[]
  onChange: (value: string[]) => void
}

export function ProviderFilter({ value, onChange }: ProviderFilterProps) {
  const [open, setOpen] = useState(false)
  const [providers, setProviders] = useState<ProviderInstance[]>([])
  const [loading, setLoading] = useState(false)
  const [hasInitialized, setHasInitialized] = useState(false)

  useEffect(() => {
    const fetchProviders = async () => {
      try {
        setLoading(true)
        const { data, error } = await providersApi.list()
        if (!error && data) {
          // Filter to only active providers
          const activeProviders = data.filter((p) => p.is_active)
          setProviders(activeProviders)
        }
      } finally {
        setLoading(false)
      }
    }
    fetchProviders()
  }, [])
  const handleProviderToggle = (providerName: string) => {
    const newValue = value.includes(providerName)
      ? value.filter((p) => p !== providerName)
      : [...value, providerName]
    onChange(newValue)
  }

  const handleSelectAll = () => {
    onChange(providers.map((p) => p.name))
  }

  const displayText = () => {
    if (loading) return 'Loading...'
    if (value.length === 0) return 'All Providers'
    if (value.length === providers.length) return 'All Providers'
    return `${value.length} Provider${value.length === 1 ? '' : 's'} Selected`
  }

  const handleClearAll = () => {
    onChange([])
  }

  const getProviderDisplayName = (provider: ProviderInstance) => {
    return provider.display_name || provider.name || provider.provider_type
  }

  useEffect(() => {
    if (
      !hasInitialized &&
      !loading &&
      providers.length > 0 &&
      value.length === 0
    ) {
      onChange(providers.map((p) => p.name))
      setHasInitialized(true)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasInitialized, loading, providers.length, value.length])

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant='outline'
          role='combobox'
          aria-expanded={open}
          className='min-w-[200px] justify-between'
          disabled={loading}
        >
          {displayText()}
          <ChevronsUpDown className='ml-2 h-4 w-4 shrink-0 opacity-50' />
        </Button>
      </PopoverTrigger>
      <PopoverContent className='w-[300px] p-0' align='start'>
        <Command>
          <CommandInput placeholder='Search providers...' />
          <CommandList>
            <CommandEmpty>
              {loading ? 'Loading providers...' : 'No providers found.'}
            </CommandEmpty>
            {!loading && providers.length > 0 && (
              <CommandGroup>
                <div className='flex items-center justify-between border-b px-2 py-1.5 text-sm'>
                  <span className='font-medium'>
                    Providers ({providers.length})
                  </span>
                  <div className='flex gap-2'>
                    <Button
                      variant='ghost'
                      size='sm'
                      className='hover:text-primary h-auto p-0 text-xs'
                      onClick={handleSelectAll}
                    >
                      Select All
                    </Button>
                    <Button
                      variant='ghost'
                      size='sm'
                      className='hover:text-primary h-auto p-0 text-xs'
                      onClick={handleClearAll}
                    >
                      Clear
                    </Button>
                  </div>
                </div>
                {providers.map((provider) => (
                  <CommandItem
                    key={provider.name}
                    onSelect={() => handleProviderToggle(provider.name)}
                    className='flex cursor-pointer items-center space-x-2'
                  >
                    <Checkbox
                      checked={value.includes(provider.name)}
                      onChange={() => handleProviderToggle(provider.name)}
                    />
                    <div className='flex flex-1 flex-col'>
                      <span className='text-sm'>
                        {getProviderDisplayName(provider)}
                      </span>
                      {provider.display_name && (
                        <span className='text-muted-foreground text-xs'>
                          {provider.provider_type}
                        </span>
                      )}
                    </div>
                    <Check
                      className={cn(
                        'h-4 w-4',
                        value.includes(provider.name)
                          ? 'opacity-100'
                          : 'opacity-0'
                      )}
                    />
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

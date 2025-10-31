import { useState } from 'react'
import type { Provider } from '@/lib/api'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'

interface ProviderSelectorDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  providers: Provider[]
  onSelect: (provider: Provider) => void
}

export function ProviderSelectorDialog({
  open,
  onOpenChange,
  providers,
  onSelect,
}: ProviderSelectorDialogProps) {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredProviders = providers.filter((provider) =>
    provider.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleSelect = (provider: Provider) => {
    onSelect(provider)
    setSearchTerm('')
  }

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setSearchTerm('')
    }
    onOpenChange(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className='max-w-2xl'>
        <DialogHeader>
          <DialogTitle>Select Provider</DialogTitle>
          <DialogDescription>
            Choose a provider to connect to your account
          </DialogDescription>
        </DialogHeader>

        <div className='space-y-4'>
          <Input
            placeholder='Search providers...'
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className='w-full'
          />

          <ScrollArea className='h-[400px] pr-4'>
            <div className='grid gap-3'>
              {filteredProviders.map((provider) => (
                <button
                  key={provider.provider_type}
                  className='hover:border-primary flex items-start gap-4 rounded-lg border p-4 text-left transition-all hover:shadow-md'
                  onClick={() => handleSelect(provider)}
                  type='button'
                >
                  <div className='bg-muted flex size-12 shrink-0 items-center justify-center rounded-lg p-2'>
                    {provider.logo}
                  </div>
                  <div className='flex-1 space-y-1'>
                    <h3 className='font-semibold'>{provider.name}</h3>
                    <p className='text-muted-foreground text-sm'>
                      {provider.desc}
                    </p>
                  </div>
                </button>
              ))}

              {filteredProviders.length === 0 && (
                <div className='py-12 text-center'>
                  <p className='text-muted-foreground'>
                    No providers match your search
                  </p>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  )
}

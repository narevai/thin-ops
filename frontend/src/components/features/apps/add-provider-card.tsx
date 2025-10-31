import { IconPlus } from '@tabler/icons-react'

interface AddProviderCardProps {
  onAddClick: () => void
}

export function AddProviderCard({ onAddClick }: AddProviderCardProps) {
  return (
    <li className='flex h-full flex-col rounded-lg border border-dashed p-4 transition-all hover:border-solid hover:shadow-md'>
      <button
        className='flex size-full flex-col items-center justify-center gap-3'
        onClick={onAddClick}
        type='button'
      >
        <div className='bg-muted hover:bg-muted/80 flex size-12 items-center justify-center rounded-lg transition-colors'>
          <IconPlus size={24} className='text-muted-foreground' />
        </div>
        <div className='text-center'>
          <h2 className='mb-0.5 font-semibold'>Connect</h2>
          <p className='text-sm text-gray-500'>
            Connect a new billing provider
          </p>
        </div>
      </button>
    </li>
  )
}

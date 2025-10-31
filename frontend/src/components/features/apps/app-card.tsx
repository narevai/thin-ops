import { IconSettings, IconTestPipe, IconTrash } from '@tabler/icons-react'
import type { Provider, ProviderInstance } from '@/lib/api'
import { Button } from '@/components/ui/button'

interface AppCardProps {
  app: Provider
  instance: ProviderInstance | null
  demoMode: boolean
  onConnect: (app: Provider) => void
  onEdit: (app: Provider, instance: ProviderInstance) => void
  onTest: (instance: ProviderInstance) => void
  onDelete: (instance: ProviderInstance) => void
}

export function AppCard({
  app,
  instance,
  demoMode,
  onConnect,
  onEdit,
  onTest,
  onDelete,
}: AppCardProps) {
  return (
    <li
      key={`${app.provider_type}-${app.name}`}
      className='rounded-lg border p-4 transition-shadow hover:shadow-md'
    >
      <div className='mb-8 flex items-center justify-between'>
        <div className='bg-muted flex size-10 items-center justify-center rounded-lg p-2'>
          {app.logo}
        </div>
        {app.connected && instance ? (
          <div className='flex items-center gap-2'>
            <Button
              variant='ghost'
              size='icon'
              className='size-8'
              onClick={() => onEdit(app, instance)}
              title='Edit provider'
            >
              <IconSettings size={16} />
            </Button>
            <Button
              variant='ghost'
              size='icon'
              className='size-8'
              onClick={() => onTest(instance)}
              title='Test connection'
            >
              <IconTestPipe size={16} />
            </Button>
            <Button
              variant='ghost'
              size='icon'
              className='size-8 text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950 dark:hover:text-red-300'
              onClick={() => onDelete(instance)}
              title='Delete provider'
            >
              <IconTrash size={16} />
            </Button>
          </div>
        ) : (
          <Button
            variant='outline'
            size='sm'
            disabled={demoMode}
            onClick={() => onConnect(app)}
          >
            Connect
          </Button>
        )}
      </div>
      <div>
        <h2 className='mb-1 font-semibold'>{app.name}</h2>
        <p className='line-clamp-2 text-gray-500'>{app.desc}</p>
      </div>
    </li>
  )
}

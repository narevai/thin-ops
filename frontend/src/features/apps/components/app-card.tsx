import {
  IconSettings,
  IconTestPipe,
  IconTrash,
  IconAlertCircle,
} from '@tabler/icons-react'
import type { Provider, ProviderInstance } from '@/lib/api'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface AppCardProps {
  app: Provider
  instance: ProviderInstance | null
  onEdit: (app: Provider, instance: ProviderInstance) => void
  onTest: (instance: ProviderInstance) => void
  onDelete: (instance: ProviderInstance) => void
}

export function AppCard({
  app,
  instance,
  onEdit,
  onTest,
  onDelete,
}: AppCardProps) {
  const isInactive = instance && !instance.is_active

  return (
    <li
      key={`${app.provider_type}-${app.name}`}
      className={`flex h-full flex-col rounded-lg border p-4 transition-shadow hover:shadow-md ${
        isInactive
          ? 'border-orange-200 bg-orange-50/50 dark:border-orange-800 dark:bg-orange-950/20'
          : ''
      }`}
    >
      <div className='mb-auto flex items-center justify-between pb-4'>
        <div className='bg-muted flex size-10 items-center justify-center rounded-lg p-2'>
          {app.logo}
        </div>
        {instance && (
          <div className='flex items-center gap-1'>
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
        )}
      </div>
      <div>
        <div className='mb-0.5 flex items-center gap-2'>
          <h2 className='font-semibold'>
            {instance?.display_name || instance?.name || app.name}
          </h2>
          {isInactive && (
            <Badge
              variant='outline'
              className='border-orange-400 text-orange-700 dark:border-orange-600 dark:text-orange-400'
            >
              <IconAlertCircle size={12} className='mr-1' />
              Inactive
            </Badge>
          )}
        </div>
        <p className='text-muted-foreground line-clamp-2 text-sm'>{app.name}</p>
        {isInactive && instance.validation_error && (
          <p
            className='mt-1 line-clamp-1 text-xs text-orange-600 dark:text-orange-400'
            title={instance.validation_error}
          >
            {instance.validation_error}
          </p>
        )}
      </div>
    </li>
  )
}

import { useState, useEffect } from 'react'
import {
  IconAdjustmentsHorizontal,
  IconSortAscendingLetters,
  IconSortDescendingLetters,
  IconSettings,
  IconTestPipe,
  IconTrash,
} from '@tabler/icons-react'
import { toast } from 'sonner'
import type {
  CreateProviderRequest,
  Provider,
  ProviderInstance,
  UpdateProviderRequest,
} from '@/lib/api'
import { useConfig } from '@/hooks/use-config'
import { useProviders } from '@/hooks/use-providers'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProviderDialogManager } from '@/components/provider-dialogs/provider-dialog-manager'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'

const appText = new Map<string, string>([
  ['all', 'All Apps'],
  ['connected', 'Connected'],
  ['notConnected', 'Not Connected'],
])

export default function Apps() {
  const [sort, setSort] = useState<'ascending' | 'descending'>('ascending')
  const [appType, setAppType] = useState<'all' | 'connected' | 'notConnected'>(
    'all'
  )
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedApp, setSelectedApp] = useState<Provider | null>(null)
  const [selectedInstance, setSelectedInstance] =
    useState<ProviderInstance | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [instanceToDelete, setInstanceToDelete] =
    useState<ProviderInstance | null>(null)

  const {
    providers: apps,
    providerInstances,
    loading,
    createProvider,
    updateProvider,
    deleteProvider,
    testProvider,
  } = useProviders()
  const { getConfig } = useConfig()
  const [demoMode, setDemoMode] = useState<boolean>(false)

  useEffect(() => {
    ;(async () => {
      const config = await getConfig()
      const settings = (config as unknown as { settings?: { demo?: unknown } })
        ?.settings
      const demo = settings?.demo
      if (typeof demo === 'boolean') {
        setDemoMode(demo)
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const filteredApps = apps
    .sort((a, b) =>
      sort === 'ascending'
        ? a.name.localeCompare(b.name)
        : b.name.localeCompare(a.name)
    )
    .filter((app) =>
      appType === 'connected'
        ? app.connected
        : appType === 'notConnected'
          ? !app.connected
          : true
    )
    .filter((app) => app.name.toLowerCase().includes(searchTerm.toLowerCase()))

  const handleConnectClick = (app: Provider) => {
    if (!app.connected) {
      setSelectedApp(app)
      setDialogMode('create')
      setDialogOpen(true)
    }
  }

  const handleEditClick = (app: Provider, instance: ProviderInstance) => {
    setSelectedApp(app)
    setSelectedInstance(instance)
    setDialogMode('edit')
    setDialogOpen(true)
  }

  const handleTestClick = async (instance: ProviderInstance) => {
    try {
      await testProvider(instance.id)
      toast.success('Connection test successful!', {
        description: `${instance.display_name || instance.name} is working correctly`,
      })
    } catch (_) {
      // Error toast is handled in the testProvider function
    }
  }

  const handleDeleteClick = (instance: ProviderInstance) => {
    setInstanceToDelete(instance)
    setDeleteDialogOpen(true)
  }

  const handleConfirmDelete = async () => {
    if (!instanceToDelete) return

    try {
      await deleteProvider(instanceToDelete.id)
      toast.success('Provider deleted successfully!')
      setDeleteDialogOpen(false)
      setInstanceToDelete(null)
    } catch (_) {
      // Error toast is handled in the deleteProvider function
    }
  }

  const handleConnect = async (data: CreateProviderRequest) => {
    try {
      await createProvider(data)
      toast.success('Provider connected successfully!')
      setDialogOpen(false)
      setSelectedApp(null)
    } catch (_) {
      // Error toast is handled in the createProvider function
    }
  }

  const handleUpdate = async (id: string, data: UpdateProviderRequest) => {
    try {
      await updateProvider(id, data)
      toast.success('Provider updated successfully!')
      setDialogOpen(false)
      setSelectedApp(null)
      setSelectedInstance(null)
    } catch (_) {
      // Error toast is handled in the updateProvider function
    }
  }

  const handleDialogClose = (open: boolean) => {
    setDialogOpen(open)
    if (!open) {
      setSelectedApp(null)
      setSelectedInstance(null)
    }
  }

  // Helper to get the first active instance for a provider type
  const getProviderInstance = (
    providerType: string
  ): ProviderInstance | null => {
    return (
      providerInstances.find(
        (instance) =>
          instance.provider_type === providerType && instance.is_active
      ) || null
    )
  }

  return (
    <>
      <Header>
        <Search />
        <div className='ml-auto flex items-center gap-4'>
          <ThemeSwitch />
        </div>
      </Header>

      <Main fixed>
        {demoMode && (
          <Alert className='mb-6 border-orange-200 bg-orange-50 text-orange-800 dark:border-orange-800 dark:bg-orange-950 dark:text-orange-200'>
            <AlertDescription>
              You're viewing demo data. To connect real providers, please
              disable demo mode in your configuration and follow the{' '}
              <a
                href='https://narev.ai/docs'
                className='underline hover:no-underline'
              >
                setup documentation
              </a>
            </AlertDescription>
          </Alert>
        )}
        <div>
          <h1 className='text-2xl font-bold tracking-tight'>
            Provider Integrations
          </h1>
          <p className='text-muted-foreground'>
            Connect your billing providers to start analyzing costs and usage
          </p>
        </div>

        <div className='my-4 flex items-end justify-between sm:my-0 sm:items-center'>
          <div className='flex flex-col gap-4 sm:my-4 sm:flex-row'>
            <Input
              placeholder='Filter providers...'
              className='h-9 w-40 lg:w-[250px]'
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Select
              value={appType}
              onValueChange={(value: 'all' | 'connected' | 'notConnected') =>
                setAppType(value)
              }
            >
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

          <Select
            value={sort}
            onValueChange={(value: 'ascending' | 'descending') =>
              setSort(value)
            }
          >
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

        <Separator className='shadow-sm' />

        {loading ? (
          <div className='grid gap-4 pt-4 md:grid-cols-2 lg:grid-cols-3'>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className='rounded-lg border p-4'>
                <div className='mb-8 flex items-center justify-between'>
                  <Skeleton className='h-10 w-10 rounded-lg' />
                  <Skeleton className='h-8 w-20' />
                </div>
                <div>
                  <Skeleton className='mb-2 h-5 w-32' />
                  <Skeleton className='h-4 w-full' />
                  <Skeleton className='mt-1 h-4 w-3/4' />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <ul className='faded-bottom no-scrollbar grid gap-4 overflow-auto pt-4 pb-16 md:grid-cols-2 lg:grid-cols-3'>
            {filteredApps.map((app) => {
              const instance = getProviderInstance(app.provider_type)
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
                          onClick={() => handleEditClick(app, instance)}
                          title='Edit provider'
                        >
                          <IconSettings size={16} />
                        </Button>
                        <Button
                          variant='ghost'
                          size='icon'
                          className='size-8'
                          onClick={() => handleTestClick(instance)}
                          title='Test connection'
                        >
                          <IconTestPipe size={16} />
                        </Button>
                        <Button
                          variant='ghost'
                          size='icon'
                          className='size-8 text-red-600 hover:bg-red-50 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-950 dark:hover:text-red-300'
                          onClick={() => handleDeleteClick(instance)}
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
                        onClick={() => handleConnectClick(app)}
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
            })}
          </ul>
        )}

        {!loading && filteredApps.length === 0 && (
          <div className='py-12 text-center'>
            <p className='text-muted-foreground'>
              {searchTerm || appType !== 'all'
                ? 'No providers match your filters'
                : 'No providers available'}
            </p>
          </div>
        )}
      </Main>

      {dialogMode === 'create' ? (
        <ProviderDialogManager
          mode='create'
          open={dialogOpen}
          onOpenChange={handleDialogClose}
          provider={selectedApp}
          onConnect={handleConnect}
        />
      ) : (
        <ProviderDialogManager
          mode='edit'
          open={dialogOpen}
          onOpenChange={handleDialogClose}
          provider={selectedApp}
          providerInstance={selectedInstance!}
          onUpdate={handleUpdate}
        />
      )}

      <ConfirmDialog
        open={deleteDialogOpen}
        onOpenChange={setDeleteDialogOpen}
        title='Delete Provider'
        desc={`Are you sure you want to delete ${instanceToDelete?.display_name || instanceToDelete?.name}? This action cannot be undone.`}
        confirmText='Delete'
        destructive
        handleConfirm={handleConfirmDelete}
      />
    </>
  )
}

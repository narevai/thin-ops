import { useState, useEffect } from 'react'
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
import { Separator } from '@/components/ui/separator'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { AppCard } from '@/components/features/apps/app-card'
import { AppsEmptyState } from '@/components/features/apps/apps-empty-state'
import { AppsFilters } from '@/components/features/apps/apps-filters'
import { AppsLoadingSkeleton } from '@/components/features/apps/apps-loading-skeleton'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProviderDialogManager } from '@/components/provider-dialogs/provider-dialog-manager'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'

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

        <AppsFilters
          searchTerm={searchTerm}
          appType={appType}
          sort={sort}
          onSearchChange={setSearchTerm}
          onAppTypeChange={setAppType}
          onSortChange={setSort}
        />

        <Separator className='shadow-sm' />

        {loading ? (
          <AppsLoadingSkeleton />
        ) : (
          <ul className='faded-bottom no-scrollbar grid gap-4 overflow-auto pt-4 pb-16 md:grid-cols-2 lg:grid-cols-3'>
            {filteredApps.map((app) => {
              const instance = getProviderInstance(app.provider_type)
              return (
                <AppCard
                  key={`${app.provider_type}-${app.name}`}
                  app={app}
                  instance={instance}
                  demoMode={demoMode}
                  onConnect={handleConnectClick}
                  onEdit={handleEditClick}
                  onTest={handleTestClick}
                  onDelete={handleDeleteClick}
                />
              )
            })}
          </ul>
        )}

        {!loading && filteredApps.length === 0 && (
          <AppsEmptyState searchTerm={searchTerm} appType={appType} />
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

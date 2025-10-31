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
import { AddProviderCard } from '@/components/features/apps/add-provider-card'
import { AppCard } from '@/components/features/apps/app-card'
import { AppsEmptyState } from '@/components/features/apps/apps-empty-state'
import { AppsFilters } from '@/components/features/apps/apps-filters'
import { AppsLoadingSkeleton } from '@/components/features/apps/apps-loading-skeleton'
import { ProviderDialogManager } from '@/components/features/apps/dialogs/provider-dialog-manager'
import { ProviderSelectorDialog } from '@/components/features/apps/dialogs/provider-selector-dialog'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
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
  const [selectorDialogOpen, setSelectorDialogOpen] = useState(false)

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

  // Get all active provider instances with their provider info
  const activeInstances = providerInstances
    .filter((instance) => instance.is_active)
    .map((instance) => {
      const provider = apps.find(
        (app) => app.provider_type === instance.provider_type
      )
      return { instance, provider }
    })
    .filter((item) => item.provider !== undefined)

  // Filter and sort instances based on search and sort preferences
  const filteredInstances = activeInstances
    .filter(
      ({ instance, provider }) =>
        provider!.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        instance.display_name
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        instance.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      const nameA = a.instance.display_name || a.provider!.name
      const nameB = b.instance.display_name || b.provider!.name
      return sort === 'ascending'
        ? nameA.localeCompare(nameB)
        : nameB.localeCompare(nameA)
    })

  const handleAddProviderClick = () => {
    if (demoMode) {
      toast.error('Cannot add providers in demo mode', {
        description:
          'To connect real providers, please disable demo mode in your configuration.',
      })
      return
    }

    setSelectorDialogOpen(true)
  }

  const handleProviderSelect = (app: Provider) => {
    setSelectedApp(app)
    setDialogMode('create')
    setSelectorDialogOpen(false)
    setDialogOpen(true)
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
          <ul className='faded-bottom no-scrollbar grid auto-rows-fr gap-4 overflow-auto pt-4 pb-16 md:grid-cols-2 lg:grid-cols-3'>
            <AddProviderCard onAddClick={handleAddProviderClick} />
            {filteredInstances.map(({ instance, provider }) => (
              <AppCard
                key={instance.id}
                app={provider!}
                instance={instance}
                onEdit={handleEditClick}
                onTest={handleTestClick}
                onDelete={handleDeleteClick}
              />
            ))}
          </ul>
        )}

        {!loading && filteredInstances.length === 0 && (
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

      <ProviderSelectorDialog
        open={selectorDialogOpen}
        onOpenChange={setSelectorDialogOpen}
        providers={apps}
        onSelect={handleProviderSelect}
      />

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

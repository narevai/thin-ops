import type {
  CreateProviderRequest,
  Provider,
  ProviderInstance,
  UpdateProviderRequest,
} from '@/lib/api'
import { ProviderDialog } from './provider-dialog'
import { ProviderEditDialog } from './provider-edit-dialog'

interface BaseProviderDialogManagerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  provider: Provider | null
}

interface CreateModeProps extends BaseProviderDialogManagerProps {
  mode: 'create'
  providerInstance?: never
  onConnect: (data: CreateProviderRequest) => Promise<void>
  onUpdate?: never
}

interface EditModeProps extends BaseProviderDialogManagerProps {
  mode: 'edit'
  providerInstance: ProviderInstance
  onConnect?: never
  onUpdate: (id: string, data: UpdateProviderRequest) => Promise<void>
}

type ProviderDialogManagerProps = CreateModeProps | EditModeProps

export function ProviderDialogManager(props: ProviderDialogManagerProps) {
  if (props.mode === 'edit') {
    return (
      <ProviderEditDialog
        open={props.open}
        onOpenChange={props.onOpenChange}
        provider={props.provider}
        providerInstance={props.providerInstance}
        onUpdate={props.onUpdate}
      />
    )
  }

  return (
    <ProviderDialog
      open={props.open}
      onOpenChange={props.onOpenChange}
      provider={props.provider}
      onConnect={props.onConnect}
    />
  )
}

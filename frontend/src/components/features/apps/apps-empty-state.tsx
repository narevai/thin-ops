interface AppsEmptyStateProps {
  searchTerm: string
  appType: 'all' | 'connected' | 'notConnected'
}

export function AppsEmptyState({ searchTerm, appType }: AppsEmptyStateProps) {
  return (
    <div className='py-12 text-center'>
      <p className='text-muted-foreground'>
        {searchTerm || appType !== 'all'
          ? 'No providers match your filters'
          : 'No providers available'}
      </p>
    </div>
  )
}

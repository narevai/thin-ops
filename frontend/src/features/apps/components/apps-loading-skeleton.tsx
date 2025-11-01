import { Skeleton } from '@/components/ui/skeleton'

export function AppsLoadingSkeleton() {
  return (
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
  )
}

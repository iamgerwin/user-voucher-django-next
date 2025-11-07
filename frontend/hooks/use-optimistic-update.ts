import { useState, useCallback } from 'react';

export interface OptimisticUpdateOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  onSettled?: () => void;
}

export function useOptimisticUpdate<T>(initialData: T | null) {
  const [data, setData] = useState<T | null>(initialData);
  const [isOptimistic, setIsOptimistic] = useState(false);

  const optimisticUpdate = useCallback(
    async (
      optimisticData: T,
      mutationFn: () => Promise<T>,
      options?: OptimisticUpdateOptions<T>
    ) => {
      const previousData = data;

      // Immediately update with optimistic data
      setData(optimisticData);
      setIsOptimistic(true);

      try {
        // Perform the actual mutation
        const result = await mutationFn();

        // Update with real data from server
        setData(result);
        options?.onSuccess?.(result);

        return result;
      } catch (error) {
        // Rollback to previous data on error
        setData(previousData);
        options?.onError?.(error as Error);
        throw error;
      } finally {
        setIsOptimistic(false);
        options?.onSettled?.();
      }
    },
    [data]
  );

  return {
    data,
    setData,
    isOptimistic,
    optimisticUpdate,
  };
}

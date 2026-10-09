import { useEffect, useState } from 'react';

export function useResource<T>(load: () => Promise<T>, key: string) {
  const [state, setState] = useState<{ key: string; data: T | null; error: string }>({ key: '', data: null, error: '' });
  useEffect(() => {
    let active = true;
    load().then(data => { if (active) setState({ key, data, error: '' }); })
      .catch(error => { if (active) setState({ key, data: null, error: error instanceof Error ? error.message : 'Unable to load API data.' }); });
    return () => { active = false; };
  }, [load, key]);
  return state.key === key ? state : { key, data: null, error: '' };
}

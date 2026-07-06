export type SummaryStatus = 'pending' | 'running' | 'ready' | 'failed';

export interface Summary {
  id: number;
  content: string;
  status: SummaryStatus;
  created_at: string;
  updated_at: string;
}

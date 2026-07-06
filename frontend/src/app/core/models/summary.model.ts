export type SummaryStatus = 'pending' | 'ready' | 'failed';

export interface Summary {
  id: number;
  content: string;
  status: SummaryStatus;
  created_at: string;
  updated_at: string;
}

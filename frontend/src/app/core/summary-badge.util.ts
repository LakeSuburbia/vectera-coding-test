import { SummaryStatus } from './models/summary.model';

const BADGE_CLASSES: Record<SummaryStatus | 'none', string> = {
  ready: 'bg-success',
  pending: 'bg-warning text-dark',
  running: 'bg-warning text-dark',
  failed: 'bg-danger',
  none: 'bg-secondary',
};

export function summaryBadgeClass(status: SummaryStatus | 'none'): string {
  return BADGE_CLASSES[status];
}

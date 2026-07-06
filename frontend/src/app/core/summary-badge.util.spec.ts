import { summaryBadgeClass } from './summary-badge.util';
import { SummaryStatus } from './models/summary.model';

describe('summaryBadgeClass', () => {
  const cases: Array<{ status: SummaryStatus | 'none'; expected: string }> = [
    { status: 'ready', expected: 'bg-success' },
    { status: 'pending', expected: 'bg-warning text-dark' },
    { status: 'failed', expected: 'bg-danger' },
    { status: 'none', expected: 'bg-secondary' },
  ];

  cases.forEach(({ status, expected }) => {
    it(`maps "${status}" to "${expected}"`, () => {
      expect(summaryBadgeClass(status)).toBe(expected);
    });
  });
});

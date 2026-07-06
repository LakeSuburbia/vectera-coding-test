import { Summary } from './summary.model';

export interface Meeting {
  id: number;
  title: string;
  started_at: string;
  created_at: string;
  note_count: number;
  latest_summary: Summary | null;
}

export interface CreateMeetingPayload {
  title: string;
  started_at: string;
}

import { Component, OnInit } from '@angular/core';

import { Meeting, CreateMeetingPayload } from '../../core/models/meeting.model';
import { SummaryStatus } from '../../core/models/summary.model';
import { MeetingService } from '../../core/services/meeting.service';
import { summaryBadgeClass as badgeClassFor } from '../../core/summary-badge.util';

@Component({
  selector: 'app-meeting-list',
  templateUrl: './meeting-list.component.html',
})
export class MeetingListComponent implements OnInit {
  meetings: Meeting[] = [];
  loading = false;
  error: string | null = null;

  page = 1;
  hasNext = false;
  hasPrevious = false;

  newMeeting: CreateMeetingPayload = { title: '', started_at: '' };
  creating = false;
  createError: string | null = null;

  constructor(private meetingService: MeetingService) {}

  ngOnInit(): void {
    this.loadMeetings(1);
  }

  loadMeetings(page: number): void {
    this.loading = true;
    this.error = null;
    this.meetingService.getMeetings(page).subscribe({
      next: (response) => {
        this.meetings = response.results;
        this.hasNext = !!response.next;
        this.hasPrevious = !!response.previous;
        this.page = page;
        this.loading = false;
      },
      error: () => {
        this.error = 'Failed to load meetings.';
        this.loading = false;
      },
    });
  }

  nextPage(): void {
    if (this.hasNext) this.loadMeetings(this.page + 1);
  }

  previousPage(): void {
    if (this.hasPrevious) this.loadMeetings(this.page - 1);
  }

  summaryBadge(meeting: Meeting): SummaryStatus | 'none' {
    return meeting.latest_summary?.status ?? 'none';
  }

  summaryBadgeClass(meeting: Meeting): string {
    return badgeClassFor(this.summaryBadge(meeting));
  }

  createMeeting(): void {
    if (!this.newMeeting.title || !this.newMeeting.started_at) return;
    this.creating = true;
    this.createError = null;
    this.meetingService.createMeeting(this.newMeeting).subscribe({
      next: () => {
        this.creating = false;
        this.newMeeting = { title: '', started_at: '' };
        this.loadMeetings(1);
      },
      error: () => {
        this.creating = false;
        this.createError = 'Failed to create meeting. Check the title and start date.';
      },
    });
  }
}

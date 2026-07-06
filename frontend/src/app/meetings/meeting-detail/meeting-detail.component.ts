import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { interval, Subscription } from 'rxjs';
import { startWith, switchMap, takeWhile, tap } from 'rxjs/operators';

import { Meeting } from '../../core/models/meeting.model';
import { Note, CreateNotePayload } from '../../core/models/note.model';
import { Summary, SummaryStatus } from '../../core/models/summary.model';
import { MeetingService } from '../../core/services/meeting.service';
import { summaryBadgeClass } from '../../core/summary-badge.util';

const POLL_INTERVAL_MS = 2000;

@Component({
  selector: 'app-meeting-detail',
  templateUrl: './meeting-detail.component.html',
})
export class MeetingDetailComponent implements OnInit, OnDestroy {
  meetingId!: number;
  meeting: Meeting | null = null;
  summary: Summary | null = null;

  loading = false;
  error: string | null = null;

  notes: Note[] = [];
  notesLoading = false;
  notesError: string | null = null;
  notesPage = 1;
  notesHasNext = false;

  newNote: CreateNotePayload = { author: '', text: '' };
  addingNote = false;
  addNoteError: string | null = null;

  triggeringSummary = false;
  polling = false;
  summaryActionError: string | null = null;

  private pollSub?: Subscription;

  constructor(private route: ActivatedRoute, private meetingService: MeetingService) {}

  get summaryStatus(): SummaryStatus | 'none' {
    return this.summary?.status ?? 'none';
  }

  get summaryStatusBadgeClass(): string {
    return summaryBadgeClass(this.summaryStatus);
  }

  ngOnInit(): void {
    this.meetingId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadMeeting();
    this.loadNotes(1);
  }

  ngOnDestroy(): void {
    this.pollSub?.unsubscribe();
  }

  loadMeeting(): void {
    this.loading = true;
    this.error = null;
    this.meetingService.getMeeting(this.meetingId).subscribe({
      next: (meeting) => {
        this.meeting = meeting;
        this.summary = meeting.latest_summary;
        this.loading = false;
        if (this.summary?.status === 'pending') {
          this.pollSummary();
        }
      },
      error: () => {
        this.error = 'Meeting not found.';
        this.loading = false;
      },
    });
  }

  loadNotes(page: number, append = false): void {
    this.notesLoading = true;
    this.notesError = null;
    this.meetingService.getNotes(this.meetingId, page).subscribe({
      next: (response) => {
        this.notes = append ? [...this.notes, ...response.results] : response.results;
        this.notesHasNext = !!response.next;
        this.notesPage = page;
        this.notesLoading = false;
      },
      error: () => {
        this.notesError = 'Failed to load notes.';
        this.notesLoading = false;
      },
    });
  }

  loadMoreNotes(): void {
    if (this.notesHasNext) this.loadNotes(this.notesPage + 1, true);
  }

  addNote(): void {
    if (!this.newNote.author || !this.newNote.text) return;
    this.addingNote = true;
    this.addNoteError = null;
    this.meetingService.addNote(this.meetingId, this.newNote).subscribe({
      next: (note) => {
        this.notes = [...this.notes, note];
        if (this.meeting) this.meeting.note_count += 1;
        this.newNote = { author: '', text: '' };
        this.addingNote = false;
      },
      error: () => {
        this.addingNote = false;
        this.addNoteError = 'Failed to add note.';
      },
    });
  }

  generateSummary(): void {
    this.summaryActionError = null;
    this.triggeringSummary = true;
    this.meetingService.generateSummary(this.meetingId).subscribe({
      next: () => {
        this.triggeringSummary = false;
        this.pollSummary();
      },
      error: () => {
        this.triggeringSummary = false;
        this.summaryActionError = 'Failed to generate summary.';
      },
    });
  }

  private pollSummary(): void {
    this.pollSub?.unsubscribe();
    this.polling = true;
    this.pollSub = interval(POLL_INTERVAL_MS)
      .pipe(
        startWith(0),
        switchMap(() => this.meetingService.getSummary(this.meetingId)),
        tap((summary) => (this.summary = summary)),
        takeWhile((summary) => summary.status === 'pending', true)
      )
      .subscribe({
        error: () => {
          this.summaryActionError = 'Failed to check summary status.';
          this.polling = false;
        },
        complete: () => {
          this.polling = false;
        },
      });
  }
}

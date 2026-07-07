import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { of, throwError } from 'rxjs';

import { MeetingDetailComponent } from './meeting-detail.component';
import { MeetingService } from '../../core/services/meeting.service';
import { Meeting } from '../../core/models/meeting.model';
import { Note } from '../../core/models/note.model';
import { Summary } from '../../core/models/summary.model';
import { PaginatedResponse } from '../../core/models/paginated-response.model';

function buildMeeting(overrides: Partial<Meeting> = {}): Meeting {
  return {
    id: 5,
    title: 'Sprint planning',
    started_at: '2026-07-01T10:00:00Z',
    created_at: '2026-07-01T10:00:00Z',
    note_count: 0,
    latest_summary: null,
    ...overrides,
  };
}

function buildSummary(overrides: Partial<Summary> = {}): Summary {
  return {
    id: 1,
    content: '',
    status: 'pending',
    created_at: '2026-07-01T10:00:00Z',
    updated_at: '2026-07-01T10:00:00Z',
    ...overrides,
  };
}

function buildNote(overrides: Partial<Note> = {}): Note {
  return {
    id: 1,
    author: 'Alice',
    text: 'Discussed the roadmap.',
    created_at: '2026-07-01T10:00:00Z',
    ...overrides,
  };
}

function pageOf<T>(results: T[]): PaginatedResponse<T> {
  return { count: results.length, next: null, previous: null, results };
}

describe('MeetingDetailComponent', () => {
  let component: MeetingDetailComponent;
  let meetingServiceSpy: jasmine.SpyObj<MeetingService>;

  beforeEach(() => {
    meetingServiceSpy = jasmine.createSpyObj('MeetingService', [
      'getMeeting',
      'getNotes',
      'addNote',
      'generateSummary',
      'getSummary',
    ]);
    meetingServiceSpy.getMeeting.and.returnValue(of(buildMeeting()));
    meetingServiceSpy.getNotes.and.returnValue(of(pageOf<Note>([])));

    TestBed.configureTestingModule({
      declarations: [MeetingDetailComponent],
      imports: [CommonModule, FormsModule, RouterTestingModule],
      providers: [
        { provide: MeetingService, useValue: meetingServiceSpy },
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({ id: '5' }) } } },
      ],
    });

    component = TestBed.createComponent(MeetingDetailComponent).componentInstance;
  });

  it('loads the meeting and its notes for the id from the route', () => {
    component.ngOnInit();

    expect(meetingServiceSpy.getMeeting).toHaveBeenCalledWith(5);
    expect(meetingServiceSpy.getNotes).toHaveBeenCalledWith(5, 1);
    expect(component.meeting?.title).toBe('Sprint planning');
  });

  it('sets an error message when the meeting cannot be found', () => {
    meetingServiceSpy.getMeeting.and.returnValue(throwError(() => new Error('not found')));

    component.loadMeeting();

    expect(component.error).toBe('Meeting not found.');
    expect(component.loading).toBe(false);
  });

  it('starts polling automatically when the meeting already has a pending summary', fakeAsync(() => {
    meetingServiceSpy.getMeeting.and.returnValue(
      of(buildMeeting({ latest_summary: buildSummary({ status: 'pending' }) }))
    );
    meetingServiceSpy.getSummary.and.returnValue(of(buildSummary({ status: 'ready', content: 'Done' })));

    component.meetingId = 5;
    component.loadMeeting();
    tick();

    expect(meetingServiceSpy.getSummary).toHaveBeenCalledWith(5);
    expect(component.summary?.status).toBe('ready');
    expect(component.polling).toBe(false);
  }));

  it('starts polling automatically when the meeting already has a running summary', fakeAsync(() => {
    meetingServiceSpy.getMeeting.and.returnValue(
      of(buildMeeting({ latest_summary: buildSummary({ status: 'running' }) }))
    );
    meetingServiceSpy.getSummary.and.returnValue(of(buildSummary({ status: 'ready', content: 'Done' })));

    component.meetingId = 5;
    component.loadMeeting();
    tick();

    expect(meetingServiceSpy.getSummary).toHaveBeenCalledWith(5);
    expect(component.summary?.status).toBe('ready');
    expect(component.polling).toBe(false);
  }));

  describe('addNote', () => {
    it('does not call the service when required fields are missing', () => {
      component.newNote = { author: '', text: '' };

      component.addNote();

      expect(meetingServiceSpy.addNote).not.toHaveBeenCalled();
    });

    it('appends the note and increments the note count on success', () => {
      component.meeting = buildMeeting({ note_count: 2 });
      component.newNote = { author: 'Alice', text: 'Discussed the roadmap.' };
      meetingServiceSpy.addNote.and.returnValue(of(buildNote()));

      component.addNote();

      expect(component.notes.length).toBe(1);
      expect(component.meeting?.note_count).toBe(3);
      expect(component.newNote).toEqual({ author: '', text: '' });
    });

    it('sets an error message when adding a note fails', () => {
      component.newNote = { author: 'Alice', text: 'Discussed the roadmap.' };
      meetingServiceSpy.addNote.and.returnValue(throwError(() => new Error('bad request')));

      component.addNote();

      expect(component.addNoteError).toBe('Failed to add note.');
      expect(component.addingNote).toBe(false);
    });
  });

  describe('loadMoreNotes', () => {
    it('does not request another page when there is no next page', () => {
      component.notesHasNext = false;
      meetingServiceSpy.getNotes.calls.reset();

      component.loadMoreNotes();

      expect(meetingServiceSpy.getNotes).not.toHaveBeenCalled();
    });

    it('appends the next page of notes when available', () => {
      component.meetingId = 5;
      component.notes = [buildNote({ id: 1, text: 'First' })];
      component.notesHasNext = true;
      component.notesPage = 1;
      meetingServiceSpy.getNotes.and.returnValue(of(pageOf<Note>([buildNote({ id: 2, text: 'Second' })])));

      component.loadMoreNotes();

      expect(meetingServiceSpy.getNotes).toHaveBeenCalledWith(5, 2);
      expect(component.notes.length).toBe(2);
    });
  });

  describe('generateSummary', () => {
    it('polls until the summary is ready', fakeAsync(() => {
      component.meetingId = 5;
      meetingServiceSpy.generateSummary.and.returnValue(of({ detail: 'Summary created successfully.' }));
      meetingServiceSpy.getSummary.and.returnValues(
        of(buildSummary({ status: 'running' })),
        of(buildSummary({ status: 'ready', content: 'All done' }))
      );

      component.generateSummary();
      expect(component.triggeringSummary).toBe(false);
      expect(component.polling).toBe(true);

      tick(2000);

      expect(component.summary?.status).toBe('ready');
      expect(component.summary?.content).toBe('All done');
      expect(component.polling).toBe(false);
    }));

    it('sets an error message when triggering the summary fails', () => {
      component.meetingId = 5;
      meetingServiceSpy.generateSummary.and.returnValue(throwError(() => new Error('AI unavailable')));

      component.generateSummary();

      expect(component.summaryActionError).toBe('Failed to generate summary.');
      expect(component.triggeringSummary).toBe(false);
      expect(meetingServiceSpy.getSummary).not.toHaveBeenCalled();
    });

    it('keeps polling through a single transient error and recovers', fakeAsync(() => {
      component.meetingId = 5;
      meetingServiceSpy.generateSummary.and.returnValue(of({ detail: 'ok' }));
      meetingServiceSpy.getSummary.and.returnValues(
        throwError(() => new Error('network blip')),
        of(buildSummary({ status: 'running' })),
        of(buildSummary({ status: 'ready', content: 'Recovered' }))
      );

      component.generateSummary();
      tick();
      expect(component.polling).toBe(true);
      expect(component.summaryActionError).toBeNull();

      tick(2000);
      expect(component.summary?.status).toBe('running');
      expect(component.polling).toBe(true);

      tick(2000);
      expect(component.summary?.status).toBe('ready');
      expect(component.summary?.content).toBe('Recovered');
      expect(component.polling).toBe(false);
      expect(component.summaryActionError).toBeNull();
    }));

    it('stops polling and reports failure after repeated consecutive errors', fakeAsync(() => {
      component.meetingId = 5;
      meetingServiceSpy.generateSummary.and.returnValue(of({ detail: 'ok' }));
      meetingServiceSpy.getSummary.and.returnValue(throwError(() => new Error('network down')));

      component.generateSummary();
      tick();
      expect(component.polling).toBe(true);
      expect(component.summaryActionError).toBeNull();

      tick(2000);
      expect(component.polling).toBe(true);

      tick(2000);
      expect(component.summaryActionError).toBe(
        'Failed to check summary status. Please refresh the page.'
      );
      expect(component.polling).toBe(false);
    }));
  });
});

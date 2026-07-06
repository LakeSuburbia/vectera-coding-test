import { TestBed } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { of, throwError } from 'rxjs';

import { MeetingListComponent } from './meeting-list.component';
import { MeetingService } from '../../core/services/meeting.service';
import { Meeting } from '../../core/models/meeting.model';
import { PaginatedResponse } from '../../core/models/paginated-response.model';

function buildMeeting(overrides: Partial<Meeting> = {}): Meeting {
  return {
    id: 1,
    title: 'Sprint planning',
    started_at: '2026-07-01T10:00:00Z',
    created_at: '2026-07-01T10:00:00Z',
    note_count: 0,
    latest_summary: null,
    ...overrides,
  };
}

function pageOf(
  results: Meeting[],
  next: string | null = null,
  previous: string | null = null
): PaginatedResponse<Meeting> {
  return { count: results.length, next, previous, results };
}

describe('MeetingListComponent', () => {
  let component: MeetingListComponent;
  let meetingServiceSpy: jasmine.SpyObj<MeetingService>;

  beforeEach(() => {
    meetingServiceSpy = jasmine.createSpyObj('MeetingService', ['getMeetings', 'createMeeting']);
    meetingServiceSpy.getMeetings.and.returnValue(of(pageOf([buildMeeting()])));

    TestBed.configureTestingModule({
      declarations: [MeetingListComponent],
      imports: [CommonModule, FormsModule, RouterTestingModule],
      providers: [{ provide: MeetingService, useValue: meetingServiceSpy }],
    });

    component = TestBed.createComponent(MeetingListComponent).componentInstance;
  });

  it('loads the first page of meetings on init', () => {
    component.ngOnInit();

    expect(meetingServiceSpy.getMeetings).toHaveBeenCalledWith(1);
    expect(component.meetings.length).toBe(1);
    expect(component.loading).toBe(false);
  });

  it('sets an error message when loading meetings fails', () => {
    meetingServiceSpy.getMeetings.and.returnValue(throwError(() => new Error('network down')));

    component.loadMeetings(1);

    expect(component.error).toBe('Failed to load meetings.');
    expect(component.loading).toBe(false);
  });

  it('tracks hasNext/hasPrevious from the paginated response', () => {
    meetingServiceSpy.getMeetings.and.returnValue(of(pageOf([buildMeeting()], 'page=3', 'page=1')));

    component.loadMeetings(2);

    expect(component.hasNext).toBe(true);
    expect(component.hasPrevious).toBe(true);
    expect(component.page).toBe(2);
  });

  it('does not request another page when there is no next/previous page', () => {
    component.hasNext = false;
    component.hasPrevious = false;
    meetingServiceSpy.getMeetings.calls.reset();

    component.nextPage();
    component.previousPage();

    expect(meetingServiceSpy.getMeetings).not.toHaveBeenCalled();
  });

  it('requests the next/previous page when allowed', () => {
    component.page = 2;
    component.hasNext = true;
    component.hasPrevious = true;
    meetingServiceSpy.getMeetings.and.returnValue(of(pageOf([buildMeeting()], 'page=x', 'page=y')));
    meetingServiceSpy.getMeetings.calls.reset();

    component.nextPage();
    expect(meetingServiceSpy.getMeetings).toHaveBeenCalledWith(3);

    component.previousPage();
    expect(meetingServiceSpy.getMeetings).toHaveBeenCalledWith(2);
  });

  describe('createMeeting', () => {
    it('does not call the service when required fields are missing', () => {
      component.newMeeting = { title: '', started_at: '' };

      component.createMeeting();

      expect(meetingServiceSpy.createMeeting).not.toHaveBeenCalled();
    });

    it('resets the form and reloads the first page on success', () => {
      component.newMeeting = { title: 'Retro', started_at: '2026-07-02T09:00:00Z' };
      meetingServiceSpy.createMeeting.and.returnValue(of(buildMeeting({ id: 2, title: 'Retro' })));
      meetingServiceSpy.getMeetings.calls.reset();

      component.createMeeting();

      expect(component.creating).toBe(false);
      expect(component.newMeeting).toEqual({ title: '', started_at: '' });
      expect(meetingServiceSpy.getMeetings).toHaveBeenCalledWith(1);
    });

    it('sets an error message when creation fails', () => {
      component.newMeeting = { title: 'Retro', started_at: '2026-07-02T09:00:00Z' };
      meetingServiceSpy.createMeeting.and.returnValue(throwError(() => new Error('bad request')));

      component.createMeeting();

      expect(component.creating).toBe(false);
      expect(component.createError).toBe('Failed to create meeting. Check the title and start date.');
    });
  });

  describe('summaryBadge / summaryBadgeClass', () => {
    const cases: Array<{
      latestSummary: Meeting['latest_summary'];
      expectedStatus: string;
      expectedClass: string;
    }> = [
      { latestSummary: null, expectedStatus: 'none', expectedClass: 'bg-secondary' },
      {
        latestSummary: { id: 1, content: '', status: 'pending', created_at: '', updated_at: '' },
        expectedStatus: 'pending',
        expectedClass: 'bg-warning text-dark',
      },
      {
        latestSummary: { id: 1, content: 'x', status: 'ready', created_at: '', updated_at: '' },
        expectedStatus: 'ready',
        expectedClass: 'bg-success',
      },
      {
        latestSummary: { id: 1, content: '', status: 'failed', created_at: '', updated_at: '' },
        expectedStatus: 'failed',
        expectedClass: 'bg-danger',
      },
    ];

    cases.forEach(({ latestSummary, expectedStatus, expectedClass }) => {
      it(`reports "${expectedStatus}" for a summary with status "${latestSummary?.status ?? 'none'}"`, () => {
        const meeting = buildMeeting({ latest_summary: latestSummary });

        expect(component.summaryBadge(meeting)).toBe(expectedStatus);
        expect(component.summaryBadgeClass(meeting)).toBe(expectedClass);
      });
    });
  });
});

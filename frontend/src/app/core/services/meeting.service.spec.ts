import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { MeetingService } from './meeting.service';
import { Meeting } from '../models/meeting.model';

describe('MeetingService', () => {
  let service: MeetingService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [MeetingService],
    });
    service = TestBed.inject(MeetingService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('fetches a paginated list of meetings', () => {
    const mockResponse = {
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          title: 'Standup',
          started_at: '2026-07-06T09:00:00Z',
          created_at: '2026-07-06T09:00:00Z',
          note_count: 2,
          latest_summary: null,
        } as Meeting,
      ],
    };

    service.getMeetings(1).subscribe((response) => {
      expect(response.results.length).toBe(1);
      expect(response.results[0].title).toBe('Standup');
    });

    const req = httpMock.expectOne((r) => r.url === '/api/meetings/');
    expect(req.request.method).toBe('GET');
    req.flush(mockResponse);
  });

  it('unwraps the summary payload nested under "detail"', () => {
    const mockSummary = { id: 1, content: 'Recap', status: 'ready', created_at: 'x', updated_at: 'y' };

    service.getSummary(1).subscribe((summary) => {
      expect(summary.status).toBe('ready');
      expect(summary.content).toBe('Recap');
    });

    const req = httpMock.expectOne((r) => r.url === '/api/meetings/1/summary/');
    expect(req.request.method).toBe('GET');
    req.flush({ detail: mockSummary });
  });

  it('posts a new note to the correct endpoint', () => {
    const mockNote = { id: 5, author: 'Sam', text: 'Hello', created_at: 'x' };

    service.addNote(1, { author: 'Sam', text: 'Hello' }).subscribe((note) => {
      expect(note.id).toBe(5);
    });

    const req = httpMock.expectOne((r) => r.url === '/api/meetings/1/notes/');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ author: 'Sam', text: 'Hello' });
    req.flush(mockNote);
  });
});

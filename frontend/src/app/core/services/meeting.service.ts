import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Meeting, CreateMeetingPayload } from '../models/meeting.model';
import { Note, CreateNotePayload } from '../models/note.model';
import { Summary } from '../models/summary.model';
import { PaginatedResponse } from '../models/paginated-response.model';

@Injectable({ providedIn: 'root' })
export class MeetingService {
  private readonly baseUrl = '/api/meetings';

  constructor(private http: HttpClient) {}

  getMeetings(page = 1): Observable<PaginatedResponse<Meeting>> {
    return this.http.get<PaginatedResponse<Meeting>>(`${this.baseUrl}/`, {
      params: { page },
    });
  }

  getMeeting(id: number): Observable<Meeting> {
    return this.http.get<Meeting>(`${this.baseUrl}/${id}/`);
  }

  createMeeting(payload: CreateMeetingPayload): Observable<Meeting> {
    return this.http.post<Meeting>(`${this.baseUrl}/`, payload);
  }

  getNotes(meetingId: number, page = 1): Observable<PaginatedResponse<Note>> {
    return this.http.get<PaginatedResponse<Note>>(`${this.baseUrl}/${meetingId}/notes/`, {
      params: { page },
    });
  }

  addNote(meetingId: number, payload: CreateNotePayload): Observable<Note> {
    return this.http.post<Note>(`${this.baseUrl}/${meetingId}/notes/`, payload);
  }

  generateSummary(meetingId: number): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.baseUrl}/${meetingId}/summarize/`, {});
  }

  getSummary(meetingId: number): Observable<Summary> {
    return this.http
      .get<{ detail: Summary }>(`${this.baseUrl}/${meetingId}/summary/`)
      .pipe(map((response) => response.detail));
  }
}

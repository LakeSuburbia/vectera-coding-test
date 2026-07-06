export interface Note {
  id: number;
  author: string;
  text: string;
  created_at: string;
}

export interface CreateNotePayload {
  author: string;
  text: string;
}

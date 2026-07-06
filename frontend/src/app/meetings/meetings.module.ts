import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { MeetingListComponent } from './meeting-list/meeting-list.component';
import { MeetingDetailComponent } from './meeting-detail/meeting-detail.component';

const routes: Routes = [
  { path: '', component: MeetingListComponent },
  { path: ':id', component: MeetingDetailComponent },
];

@NgModule({
  declarations: [MeetingListComponent, MeetingDetailComponent],
  imports: [CommonModule, FormsModule, RouterModule.forChild(routes)],
})
export class MeetingsModule {}

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { FormsModule } from '@angular/forms';

const routes: Routes = [
  { path: '', redirectTo: 'meetings', pathMatch: 'full' },
  {
    path: 'meetings',
    loadChildren: () => import('./meetings/meetings.module').then((m) => m.MeetingsModule),
  },
];

@NgModule({
  declarations: [AppComponent],
  imports: [BrowserModule, HttpClientModule, FormsModule, RouterModule.forRoot(routes)],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}

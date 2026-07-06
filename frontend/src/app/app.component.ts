import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <nav class="navbar navbar-expand navbar-dark bg-dark mb-4">
      <div class="container">
        <a class="navbar-brand" routerLink="/meetings">Vectera Coding Test</a>
        <div class="navbar-nav">
          <a class="nav-link" routerLink="/meetings">Meetings</a>
        </div>
      </div>
    </nav>
    <main class="container pb-5">
      <router-outlet></router-outlet>
    </main>
  `
})
export class AppComponent {}

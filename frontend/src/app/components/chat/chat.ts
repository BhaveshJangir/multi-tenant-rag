import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './chat.html',
})
export class ChatComponent implements OnInit {
  messages: any[] = [];
  currentMessage = '';
  sessionId: string | null = null;
  isLoading = false;

  constructor(private http: HttpClient, public auth: AuthService, private router: Router) {}

  ngOnInit(): void {
    if (!this.auth.isLoggedIn) {
      this.router.navigate(['/login']);
    }
    // Greet user
    this.messages.push({ role: 'assistant', content: 'Hello! I am your Enterprise Knowledge Assistant. How can I help you today?' });
  }

  sendMessage() {
    if (!this.currentMessage.trim()) return;

    const userMessage = { role: 'user', content: this.currentMessage };
    this.messages.push(userMessage);
    
    const queryPayload = {
      query: this.currentMessage,
      session_id: this.sessionId
    };

    this.currentMessage = '';
    this.isLoading = true;

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.token}`
    });

    this.http.post('http://localhost:8000/api/v1/chat', queryPayload, { headers }).subscribe({
      next: (res: any) => {
        this.sessionId = res.session_id;
        this.messages.push({ role: 'assistant', content: res.response });
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.messages.push({ role: 'assistant', content: 'Sorry, an error occurred while processing your request.' });
        this.isLoading = false;
      }
    });
  }

  logout() {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './admin-dashboard.html',
})
export class AdminDashboardComponent implements OnInit {
  documents: any[] = [];
  
  constructor(private http: HttpClient, public auth: AuthService, private router: Router) {}

  ngOnInit() {
    if (!this.auth.isLoggedIn) {
      this.router.navigate(['/login']);
      return;
    }
    const headers = new HttpHeaders({ 'Authorization': `Bearer ${this.auth.token}` });
    this.http.get('http://localhost:8000/api/v1/documents/', { headers }).subscribe({
      next: (res: any) => this.documents = res,
      error: (err) => console.error(err)
    });
  }

  getTotalStorage() {
    const total = this.documents.reduce((acc, doc) => acc + (doc.metadata_?.size || 0), 0);
    if (total === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(total) / Math.log(k));
    return parseFloat((total / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './upload.html',
})
export class UploadComponent implements OnInit {
  selectedFile: File | null = null;
  isUploading = false;
  uploadSuccess = false;
  errorMessage = '';

  constructor(private http: HttpClient, private auth: AuthService, private router: Router) {}

  ngOnInit(): void {
    if (!this.auth.isLoggedIn) {
      this.router.navigate(['/login']);
    }
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0] as File;
    this.uploadSuccess = false;
    this.errorMessage = '';
  }

  onUpload() {
    if (!this.selectedFile) return;

    this.isUploading = true;
    this.uploadSuccess = false;
    this.errorMessage = '';

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.auth.token}`
    });

    this.http.post('http://localhost:8000/api/v1/documents/upload', formData, { headers }).subscribe({
      next: (res: any) => {
        this.isUploading = false;
        this.uploadSuccess = true;
        this.selectedFile = null;
      },
      error: (err) => {
        this.isUploading = false;
        this.errorMessage = err.error?.detail || 'Failed to upload document.';
        console.error(err);
      }
    });
  }
}

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, switchMap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/v1';
  private tokenSubject = new BehaviorSubject<string | null>(localStorage.getItem('token'));
  private userSubject = new BehaviorSubject<any>(JSON.parse(localStorage.getItem('user') || 'null'));
  
  constructor(private http: HttpClient) { }

  get token() { return this.tokenSubject.value; }
  get isLoggedIn() { return !!this.token; }
  get role() { return this.userSubject.value?.role?.toLowerCase() || ''; }
  get currentUser() { return this.userSubject.value; }

  login(credentials: any): Observable<any> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return this.http.post(`${this.apiUrl}/auth/login`, formData).pipe(
      switchMap((res: any) => {
        localStorage.setItem('token', res.access_token);
        this.tokenSubject.next(res.access_token);
        
        const headers = new HttpHeaders({ 'Authorization': `Bearer ${res.access_token}` });
        return this.http.get(`${this.apiUrl}/users/me`, { headers }).pipe(
          tap((user: any) => {
            localStorage.setItem('user', JSON.stringify(user));
            this.userSubject.next(user);
          })
        );
      })
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register`, userData);
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.tokenSubject.next(null);
    this.userSubject.next(null);
  }
}

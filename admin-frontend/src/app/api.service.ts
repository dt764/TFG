import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, catchError, map, of, tap, throwError } from 'rxjs';
import { NewUser, UpdateUser, User } from './interfaces/User';
import { History } from './interfaces/history';
import { environment } from '../environments/environment';

const backendUrl = environment.apiUrl;

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    withCredentials: true
  };
  

  constructor(private http: HttpClient) { }

  login(credentials: { email: string, password: string }): Observable<any> {
    const url = `${backendUrl}/admin-login`;
    return this.http.post(url, credentials, this.httpOptions)
  }
  

  getUsers(): Observable<User[]> {
    const url = `${backendUrl}/users`;
    return this.http.get<User[]>(url).pipe(
      catchError(this.handleError<User[]>('getUsers', []))
    );
  }

  getUser(id: string): Observable<User> {
    const url = `${backendUrl}/users/${id}`;
    return this.http.get<User>(url).pipe(
      catchError(this.handleError<User>(`getUser`))
    );
  }

  updateUser(user: UpdateUser, id: number): Observable<User> {
    return this.http.put<User>(`${backendUrl}/users/${id}`, user)
  }

  addUser(user: NewUser): Observable<User> {
    const url = `${backendUrl}/users`;
    return this.http.post<User>(url, user, this.httpOptions);
  }

  deleteUser(id: number): Observable<User> {
    const url = `${backendUrl}/users/${id}`;
    return this.http.delete<User>(url, this.httpOptions).pipe(
      catchError(this.handleError<User>(`deleteUser`))
    );
  }

  getHistory(): Observable<History[]> {
    const url = `${backendUrl}/history`;
    return this.http.get<History[]>(url).pipe(
      catchError(this.handleError<History[]>('getHistory', []))
    );
  }

  getUserHistory(id: string): Observable<History[]> {
    const url = `${backendUrl}/users/${id}/history`;
    return this.http.get<History[]>(url).pipe(
      catchError(this.handleError<History[]>('getHistoryUser', []))
    );
  }

  logout(): Observable<any> {
    const url = `${backendUrl}/logout`;
    return this.http.post(url, {}, this.httpOptions).pipe(
      tap(() => console.log('Logout successful')),
      catchError(this.handleError<any>('logout'))
    );
  }

   /**
 * Handle Http operation that failed.
 * Let the app continue.
 *
 * @param operation - name of the operation that failed
 * @param result - optional value to return as the observable result
 */
private handleError<T>(operation = 'operation', result?: T) {
  return (error: any): Observable<T> => {

    // TODO: send the error to remote logging infrastructure
    console.error(error); // log to console instead

    // Si es un error de validación, lo propagamos para que lo maneje el componente
    if (error.status === 400 && error.error.errors) {
      return throwError(() => error);
    }

    // Let the app keep running by returning an empty result.
    return of(result as T);
  };
}

}

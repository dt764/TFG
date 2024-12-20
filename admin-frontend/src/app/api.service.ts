import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, catchError, map, of, tap } from 'rxjs';
import { Usuario } from './interfaces/User';
import { Historial } from './interfaces/history';

const backendUrl = 'http://localhost:5000';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  httpOptions = {
    headers: new HttpHeaders({ 'Content-Type': 'application/json'
    })
  };

  constructor(private http: HttpClient) { }

  getUsers(): Observable<Usuario[]> {
    const url = `${backendUrl}/usuarios`;
    return this.http.get<Usuario[]>(url).pipe(
      catchError(this.handleError<Usuario[]>('getUsuarios', []))
    );
  }

  getUsuario(id: string): Observable<Usuario> {
    const url = `${backendUrl}/usuarios/${id}`;
    return this.http.get<Usuario>(url).pipe(
      catchError(this.handleError<Usuario>(`getUsuario`))
    );
  }

  updateUsuario(Usuario: Usuario) {
    return this.http.put<Usuario>(`${backendUrl}/usuarios/${Usuario.id}`, Usuario).pipe(
      catchError(this.handleError<Usuario>(`updateCreatedUsuario`))
    );
  }

  addUser(user: Usuario): Observable<Usuario> {
    const url = `${backendUrl}/usuarios`;
    return this.http.post<Usuario>(url, user, this.httpOptions).pipe(
      catchError(this.handleError<Usuario>(`addUser`))
    );
  }

  getHistorial(): Observable<Historial[]> {
    const url = `${backendUrl}/historial`;
    return this.http.get<Historial[]>(url).pipe(
      catchError(this.handleError<Historial[]>('getHistorial', []))
    );
  }

  getHistorialUsuario(id: string): Observable<Historial[]> {
    const url = `${backendUrl}/usuarios/${id}/historial`;
    return this.http.get<Historial[]>(url).pipe(
      catchError(this.handleError<Historial[]>('getHistorialUsuario', []))
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

    // Let the app keep running by returning an empty result.
    return of(result as T);
  };
}

}

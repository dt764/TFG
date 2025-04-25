import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../environments/environment';

export const authGuard: CanActivateFn = (route, state) => {
  const http = inject(HttpClient);
  const router = inject(Router);

  return http.get(`${environment.apiUrl}/check-admin-session`, {
    withCredentials: true
  }).pipe(
    map(() => true),
    catchError(() => of(router.createUrlTree(['/login'])))
  );
};

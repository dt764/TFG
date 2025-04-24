import { HttpInterceptorFn } from '@angular/common/http';

export const csrfInterceptor: HttpInterceptorFn = (req, next) => {
  const csrfToken = getCookie('csrf_access_token');

  const clonedReq = req.clone({
    withCredentials: true,
    setHeaders: csrfToken ? { 'X-CSRF-TOKEN': csrfToken } : {}
  });

  return next(clonedReq);
};

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

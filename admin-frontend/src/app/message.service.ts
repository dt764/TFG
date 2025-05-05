import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  private messageSource = new BehaviorSubject<string | null>(null);  // Conserva el último mensaje
  message$ = this.messageSource.asObservable();

  constructor() {}

  showMessage(message: string): void {
    this.messageSource.next(message);
  
    // Borra el mensaje automáticamente después de 3 segundos
    setTimeout(() => {
      this.clear();
    }, 3000);
  }
  

  clear(): void {
    this.messageSource.next(null);
  }
}

import { Component } from '@angular/core';
import { UpdateUser, User } from '../interfaces/User';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../api.service';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { History } from '../interfaces/history';

@Component({
  selector: 'app-user-detail',
  standalone: true,
  imports: [NgIf, FormsModule, NgFor],
  templateUrl: './user-detail.component.html',
  styleUrl: './user-detail.component.scss'
})

export class UserDetailComponent {

  user: User | undefined;
  userHistory: History[] = [];
  updateUser: UpdateUser | undefined;

  formErrors: {
    first_name?: string[];
    last_name?: string[];
    plates?: { [index: number]: string[] };
    [key: string]: any;
  } = {};
  

  successMessage: string | null = null;

  
  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService,
  ) {}

  ngOnInit(): void {
    this.getUser();
    this.getHistoryUser();
  }
  
  getUser(): void {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.apiService.getUser(id)
      .subscribe(User => {
        this.user = User;
      });
  }

  getHistoryUser(): void {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.apiService.getUserHistory(id)
      .subscribe(userHistory => {
        this.userHistory = userHistory;
      });
  }

  save(): void {
    if (this.user) {
      this.updateUser = {
        first_name: this.user.first_name,
        last_name: this.user.last_name,
        plates: this.user.plates
      };
      this.apiService.updateUser(this.updateUser, this.user.id).subscribe({
        next: (user) => {
          this.user = user;
          this.clearErrors();
          this.successMessage = 'Datos guardados correctamente ✅';
  
          // Borra el mensaje después de 3 segundos (opcional)
          setTimeout(() => {
            this.successMessage = null;
          }, 3000);
        },
        error: (err) => {
          if (err.status === 400 /*&& err.error.errors*/) {
            this.handleValidationErrors(err.error.error);
            console.log('Error de validación:', err.error.error);
          }
        }
      });
    }
  }

  handleValidationErrors(errors: any): void {
    this.formErrors = {};
    
    for (const field in errors) {
      if (field === 'plates' && typeof errors[field] === 'object' && !Array.isArray(errors[field])) {
        // Si plates tiene errores por índice
        this.formErrors['plates'] = {};
        for (const index in errors.plates) {
          (this.formErrors ['plates'] as { [index: number]: string[] })[+index] = errors.plates[index];
        }
      } else {
        this.formErrors[field] = errors[field];
      }
    }
  }
  
  
  clearErrors(): void {
    this.formErrors = {}; // Limpiamos los errores cuando la actualización es exitosa
  }
  

}

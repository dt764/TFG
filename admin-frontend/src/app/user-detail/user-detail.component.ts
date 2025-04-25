import { Component } from '@angular/core';
import { UpdateUser, User } from '../interfaces/User';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../api.service';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { History } from '../interfaces/history';
import { UpdateUser_FormErrors } from '../interfaces/form_errors';

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

  formErrors: UpdateUser_FormErrors = {}
  
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
    if (this.user && this.user.id !== undefined) {
      this.updateUser = {
        first_name: this.user.first_name,
        last_name: this.user.last_name,
        plates: this.user.plates
      };
      this.apiService.updateUser(this.updateUser, this.user.id).subscribe({
        next: (user) => {
          this.user = user;
          this.formErrors = {}; // Limpiamos los errores cuando la actualización es exitosa
          this.successMessage = 'Datos guardados correctamente ✅';
  
          // Borra el mensaje después de 3 segundos (opcional)
          setTimeout(() => {
            this.successMessage = null;
          }, 3000);
        },
        error: (err) => {
          if (err.status === 400 && err.error.error) {
            this.formErrors = err.error.error;
            console.log('Error de validación:', err.error.error);
          }
        }
      });
    }
  } 
}

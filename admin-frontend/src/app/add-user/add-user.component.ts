import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {NewUser} from '../interfaces/User'
import { ApiService } from '../api.service';
import { NewUser_FormErrors } from '../interfaces/form_errors';
import { Router } from '@angular/router';
import { NgClass, NgFor, NgIf } from '@angular/common';

@Component({
  selector: 'app-add-user',
  standalone: true,
  imports: [FormsModule, NgIf, NgFor, NgClass],
  templateUrl: './add-user.component.html',
  styleUrl: './add-user.component.scss'
})
export class AddUserComponent {

  newUser: NewUser = {

    first_name: '',
    password: '',
    email: '',
    last_name: '',
    plates: [],

  }

  errorMessage: string | null = null;

  formErrors: NewUser_FormErrors = {}

  requestIsLoading: boolean = false;  // Estado de carga

  showPassword: boolean = false;  // Control de visibilidad de la contraseña

  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;  // Cambiar el estado de visibilidad
  }

  createUser() {
    this.requestIsLoading = true;  // Iniciar carga
    this.apiService.addUser(this.newUser)
      .subscribe({
        next: (user) => {
          this.requestIsLoading = false;  // Finalizar carga
          this.router.navigate(['/users', user.id]);
          
        },
        error: (err) => {
          if (err.status === 400 /*&& err.error.errors*/) {
            this.formErrors = err.error.error;
          }
          else {
            this.errorMessage = 'No se pudo crear el usuario. Intente más tarde.';
          }
          this.requestIsLoading = false;  // Finalizar carga
        }
      });
  }

}

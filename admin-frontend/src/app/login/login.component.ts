import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ApiService } from '../api.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  errorMessage = '';
  loading = false;

  loginForm;

  showPassword = false;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  onSubmit() {
    this.errorMessage = '';
    this.loading = true;

    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();  // fuerza mostrar los errores
      this.loading = false;
      return;
    }

    const { email, password } = this.loginForm.value;

    if (!email || !password) {
      this.errorMessage = 'Email y contraseña requeridos';
      this.loading = false;
      return;
    }

    this.api.login({ email, password }).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.loading = false;
      
        if (err.status === 0) {
          this.errorMessage = 'Servidor no disponible. Intenta más tarde.';
        } else if (err.status === 500) {
          this.errorMessage = 'Error interno del servidor. Por favor, contacta con soporte.';
        } else if (err.status === 401 && err.error?.error) {
          this.errorMessage = 'Credenciales incorrectas';
        } else {
          this.errorMessage = 'Error inesperado. Intenta nuevamente.';
        }
      }
        
    });
  }
}

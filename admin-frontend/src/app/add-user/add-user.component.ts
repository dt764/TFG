import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {NewUser} from '../interfaces/User'
import { ApiService } from '../api.service';
import { NewUser_FormErrors } from '../interfaces/form_errors';
import { Router } from '@angular/router';
import { NgFor, NgIf } from '@angular/common';

@Component({
  selector: 'app-add-user',
  standalone: true,
  imports: [FormsModule, NgIf, NgFor],
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

  formErrors: NewUser_FormErrors = {}


  constructor(
    private apiService: ApiService,
    private router: Router
  ) {}

  createUser() {
    this.apiService.addUser(this.newUser)
      .subscribe({
        next: (user) => {
          this.router.navigate(['/users', user.id]);
          
        },
        error: (err) => {
          if (err.status === 400 /*&& err.error.errors*/) {
            this.formErrors = err.error.error;
            console.log('Error de validación:', err.error.error);
          }
        }
      });
  }

}

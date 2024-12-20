import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {Usuario} from '../interfaces/User'
import { ApiService } from '../api.service';

@Component({
  selector: 'app-add-user',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './add-user.component.html',
  styleUrl: './add-user.component.scss'
})
export class AddUserComponent {

  newUser: Usuario = {

    id: 0,
    nombre: '',
    correo: '',
    apellidos: '',
    matricula1: '',
    matricula2: '',

  }

  constructor(
    private apiService: ApiService,
  ) {}

  createUser() {
    this.apiService.addUser(this.newUser)
      .subscribe();
  }

}

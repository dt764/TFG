import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {User} from '../interfaces/User'
import { ApiService } from '../api.service';
import { NgFor } from '@angular/common';

@Component({
  selector: 'app-add-user',
  standalone: true,
  imports: [FormsModule, NgFor],
  templateUrl: './add-user.component.html',
  styleUrl: './add-user.component.scss'
})
export class AddUserComponent {

  newUser: User = {

    id: 0,
    first_name: '',
    email: '',
    last_name: '',
    plates: [],

  }

  constructor(
    private apiService: ApiService,
  ) {}

  createUser() {
    this.apiService.addUser(this.newUser)
      .subscribe();
  }

}

import { Component } from '@angular/core';
import { User } from '../interfaces/User';
import { ApiService } from '../api.service';
import { NgFor, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MessageService } from '../message.service';
import { FormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [
    NgFor,
    RouterLink,
    NgIf,
    FormsModule,
    NgxPaginationModule,
  ],
  templateUrl: './users.component.html',
  styleUrl: './users.component.scss'
})
export class UsersComponent {

  users: User[] = [];
  successMessage: string | null = null;
  searchTerm: string = '';

  // Paginación
  currentPage = 1;
  itemsPerPage = 5;
  pageSizeOptions = [5, 10, 20, 50];

  constructor(
    private apiService: ApiService,
    private messageService: MessageService

  ) { }

  ngOnInit(): void {
    this.getUsers();

    // Suscribirse al mensaje de éxito
    this.messageService.message$.subscribe((message) => {
      this.successMessage = message;
      
      //Eliminar el mensaje después de 3 segundos
      setTimeout(() => {
        this.successMessage = null;
      }, 3000);
    });
  }

  getUsers(): void {
    this.apiService.getUsers()
        .subscribe(users => this.users = users);
  }

  get filteredUsers() {
    const term = this.searchTerm.toLowerCase();
    return this.users.filter(user =>
      (user.first_name + ' ' + user.last_name + ' ' + user.email + ' ' + user.plates.join(' '))
        .toLowerCase()
        .includes(term)
    );
  }

}

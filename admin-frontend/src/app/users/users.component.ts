import { Component } from '@angular/core';
import { User } from '../interfaces/User';
import { ApiService } from '../api.service';
import { AsyncPipe, NgFor, NgIf } from '@angular/common';
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
    AsyncPipe
  ],
  templateUrl: './users.component.html',
  styleUrl: './users.component.scss'
})
export class UsersComponent {

  users: User[] = [];
  successMessage: string | null = null;
  errorMessage: string | undefined;
  searchTerm: string = '';

  // Paginación
  currentPage = 1;
  itemsPerPage = 5;
  pageSizeOptions = [5, 10, 20, 50];

  isLoading: boolean = false;

  constructor(
    private apiService: ApiService,
    public messageService: MessageService

  ) { }

  ngOnInit(): void {
    this.getUsers();

  }

  getUsers(): void {
    this.isLoading = true;
    this.apiService.getUsers()
        .subscribe({
          next: users => {
            this.users = users;
            this.isLoading = false;
          },
          error: () => {
            this.isLoading = false;
            this.errorMessage = 'Error al cargar los usuarios';
          }
        });
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

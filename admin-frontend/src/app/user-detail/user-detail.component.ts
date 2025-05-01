import { Component } from '@angular/core';
import { UpdateUser, User } from '../interfaces/User';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../api.service';
import { CommonModule, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { History } from '../interfaces/history';
import { UpdateUser_FormErrors } from '../interfaces/form_errors';
import { MessageService } from '../message.service';
import { NgxPaginationModule } from 'ngx-pagination';

@Component({
  selector: 'app-user-detail',
  standalone: true,
  imports: [
    NgIf,
    FormsModule,
    NgFor,
    CommonModule,
    NgxPaginationModule
  ],
  templateUrl: './user-detail.component.html',
  styleUrl: './user-detail.component.scss'
})

export class UserDetailComponent {

  user: User | undefined;
  userHistory: History[] = [];
  updateUser: UpdateUser | undefined;

  formErrors: UpdateUser_FormErrors = {}
  
  successMessage: string | null = null;
  errorMessage: string | null = null;

  confirmDelete = false;

  startDate: string = '';
  endDate: string = '';
  plate_input: any;
  filteredEntries: History[] = [];
  activeSection: 'details' | 'history' = 'details';

  isLoading: boolean = false;

  currentPage = 1;
  itemsPerPage = 10;
  pageSizeOptions = [5, 10, 25, 50];
  requestIsLoading: boolean = false;
  
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private apiService: ApiService,
    private messageService: MessageService  // Inyectar el servicio
  ) {}

  ngOnInit(): void {
    this.getUser();
    this.getHistoryUser();
  }

  switchSection(section: 'details' | 'history') {
    this.activeSection = section;
  }
  
  getUser(): void {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.isLoading = true;
    this.apiService.getUser(id).subscribe({
      next: User => {
        this.user = User;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'No se pudo cargar la información del usuario. Inténtalo más tarde.';
      }
    });
  }
  
  getHistoryUser(): void {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.isLoading = true;
    this.apiService.getUserHistory(id).subscribe({
      next: userHistory => {
        this.userHistory = userHistory.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());;
        this.filteredEntries = [...this.userHistory];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'No se pudo cargar la información del usuario. Inténtalo más tarde.';
      }
    });
  }


  save(): void {
    if (this.user && this.user.id !== undefined) {
      const cleanedPlates = this.user.plates
      .map(plate => plate.trim()) // eliminar espacios
      .filter(plate => plate !== ''); // eliminar vacíos

      this.updateUser = {
        first_name: this.user.first_name,
        last_name: this.user.last_name,
        plates: cleanedPlates
      };
      this.requestIsLoading = true;
      this.apiService.updateUser(this.updateUser, this.user.id).subscribe({
        next: (user) => {
          this.user = user;
          this.formErrors = {}; // Limpiamos los errores cuando la actualización es exitosa
          this.successMessage = 'Datos guardados correctamente ✅';
          this.requestIsLoading = false;
  
          // Borra el mensaje después de 3 segundos (opcional)
          setTimeout(() => {
            this.successMessage = null;
          }, 3000);
        },
        error: (err) => {
          if (err.status === 400 && err.error.error) {
            this.formErrors = err.error.error;
          }
          else {
            this.errorMessage = 'No se pudieron guardar los datos. Inténtalo más tarde.';
            setTimeout(() => {
              this.errorMessage = null;
            }, 3000);
          }

          this.requestIsLoading = false;
        }
      });
    }
  }

  deleteUser() {
    if (this.user){
      this.requestIsLoading = true;
      this.apiService.deleteUser(this.user.id).subscribe({
        next: () => {
          this.messageService.showMessage("Usuario eliminado correctamente  ✅.");  // Enviar el mensaje
          this.confirmDelete = false;
          this.router.navigate(['/users']);
          this.requestIsLoading = false;

        },
        error: () => {
          this.confirmDelete = false;
          this.errorMessage = 'No se pudo elminar el usuario. Inténtalo más tarde.';
          this.requestIsLoading = false;

          setTimeout(() => {
            this.errorMessage = null;
          }, 3000);
        }
      });   
    }
   
  }
  
  filterEntries() {
    this.filteredEntries = this.userHistory.filter(entry => {
      const entryDate = new Date(entry.date);
      const inDateRange = (!this.startDate || entryDate >= new Date(this.startDate)) &&
                          (!this.endDate || entryDate <= new Date(this.endDate));
      const matchesPlate = !this.plate_input || entry.plate.toLowerCase().includes(this.plate_input.toLowerCase());
      return inDateRange && matchesPlate;
    });

    this.filteredEntries.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    
    this.currentPage = 1;
  }

}

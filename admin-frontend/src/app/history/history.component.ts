import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { History } from '../interfaces/history';
import { RouterLink } from '@angular/router';
import { CommonModule, NgClass, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NgxPaginationModule } from 'ngx-pagination';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [
    RouterLink,
    NgFor,
    NgClass,
    NgIf,
    CommonModule,
    FormsModule,
    NgxPaginationModule
  ],
  templateUrl: './history.component.html',
  styleUrl: './history.component.scss',
})

export class HistoryComponent implements OnInit {

  plate_input: any;
  history_entries: History[] = [];
  filteredEntries: History[] = [];
  startDate: string = '';
  endDate: string = '';
  statusFilter: string = '';

  currentPage = 1;
  itemsPerPage = 10;
  pageSizeOptions = [5, 10, 25, 50];

  isLoading: boolean = false;
  errorMessage: string | null = null;

  constructor(private api: ApiService) {}

  loadHistory() {
    this.isLoading = true
    this.api.getHistory().subscribe({
      next: history_entries => {
        this.history_entries = history_entries;
        this.filteredEntries = [...this.history_entries];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
        this.errorMessage = 'No se pudo cargar el historial';
      }
    });
  }

  ngOnInit() {
    this.loadHistory();
  } 

  filterEntries() {
    this.filteredEntries = this.history_entries.filter(entry => {
      const dateValid = (!this.startDate || new Date(entry.date) >= new Date(this.startDate)) &&
                        (!this.endDate || new Date(entry.date) <= new Date(this.endDate));
      const plateMatch = !this.plate_input || entry.plate.toLowerCase().includes(this.plate_input.toLowerCase());
      const statusMatch =
        !this.statusFilter ||
        (this.statusFilter === 'permitido' && entry.allowed) ||
        (this.statusFilter === 'denegado' && !entry.allowed);

      return dateValid && plateMatch && statusMatch;
    });
    this.currentPage = 1;
  } 
}

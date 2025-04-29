import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { History } from '../interfaces/history';
import { RouterLink } from '@angular/router';
import { CommonModule, NgClass, NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [
    RouterLink,
    NgFor,
    NgClass,
    NgIf,
    CommonModule,
    FormsModule
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

  constructor(private api: ApiService) {}

  loadHistory() {
    this.api.getHistory().subscribe((data) => {
      this.history_entries = data;
      this.filteredEntries = [...this.history_entries];
    });
  }

  ngOnInit() {
    this.loadHistory();
  } 

  filterEntries(): void {
    let filtered = [...this.history_entries];
  
    // Filtrado por fechas
    if (this.startDate || this.endDate) {
      const start = this.startDate ? new Date(this.startDate + 'T00:00:00') : null;
      const end = this.endDate ? new Date(this.endDate + 'T23:59:59') : null;
  
      filtered = filtered.filter(entry => {
        const entryDate = new Date(entry.date);
        let isInRange = true;
  
        if (start && entryDate < start) {
          isInRange = false;
        }
  
        if (end && entryDate > end) {
          isInRange = false;
        }
  
        return isInRange;
      });
    }
  
    // Filtrado por matrícula
    if (this.plate_input) {
      filtered = filtered.filter(entry => entry.plate.includes(this.plate_input));
    }
  
    // Filtrado por estado
    if (this.statusFilter) {
      filtered = filtered.filter(entry =>
        this.statusFilter === 'permitido' ? entry.allowed : !entry.allowed
      );
    }
  
    this.filteredEntries = filtered;
  }
  
}

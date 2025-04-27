import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { History } from '../interfaces/history';
import { RouterLink } from '@angular/router';
import { NgClass, NgFor } from '@angular/common';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [RouterLink, NgFor, NgClass],
  templateUrl: './history.component.html',
  styleUrl: './history.component.scss',
})

export class HistoryComponent implements OnInit {

  history_entries: History[] = [];
  filteredEntries: History[] = [];
  startDate: string = '';
  endDate: string = '';

  constructor(private api: ApiService) {}

  loadHistory() {;
    this.api.getHistory().subscribe((data) => {
      this.history_entries = data;
      this.filteredEntries = [...this.history_entries];
    });
  }

  ngOnInit() {
    this.loadHistory();
    
  } 

  filterByDate(): void {
    // Si no se ha seleccionado ninguna fecha, mostramos todas las entradas
    if (!this.startDate && !this.endDate) {
      this.filteredEntries = [...this.history_entries];
      return;
    }

    // Convertimos las fechas de inicio y fin a objetos Date con hora 00:00:00 para startDate y 23:59:59 para endDate
    const start = this.startDate ? new Date(this.startDate + 'T00:00:00') : null;
    const end = this.endDate ? new Date(this.endDate + 'T23:59:59') : null;

    this.filteredEntries = this.history_entries.filter(entry => {
      const entryDate = new Date(entry.date);

      let isInRange = true;

      // Verificamos si la entrada está dentro del rango de fechas
      if (start && entryDate < start) {
        isInRange = false;
      }

      if (end && entryDate > end) {
        isInRange = false;
      }

      return isInRange;
    });
  }
}

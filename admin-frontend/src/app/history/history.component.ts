import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { History } from '../interfaces/history';
import { RouterLink } from '@angular/router';
import { NgFor } from '@angular/common';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [RouterLink, NgFor],
  templateUrl: './history.component.html',
  styleUrl: './history.component.scss',
})

export class HistoryComponent implements OnInit {

  history_entries: History[] = [];

  constructor(private api: ApiService) {}

  loadHistory() {;
    this.api.getHistory().subscribe((data) => {
      this.history_entries = data;
    });
  }

  ngOnInit() {
    this.loadHistory();
  } 

}

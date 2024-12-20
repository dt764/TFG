import { Component } from '@angular/core';
import { Usuario } from '../interfaces/User';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../api.service';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Historial } from '../interfaces/history';

@Component({
  selector: 'app-user-detail',
  standalone: true,
  imports: [NgIf, FormsModule, NgFor],
  templateUrl: './user-detail.component.html',
  styleUrl: './user-detail.component.scss'
})
export class UserDetailComponent {

  usuario: Usuario | undefined;
  historial_usuario: Historial[] | undefined
  
  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService,
  ) {}

  ngOnInit(): void {
    this.getUsuario();
    this.getHistorialUsuario();
  }
  
  getUsuario(): void {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.apiService.getUsuario(id)
      .subscribe(usuario => {
        this.usuario = usuario;
      });
  }

  getHistorialUsuario(): void {
    const id = String(this.route.snapshot.paramMap.get('id'));
    this.apiService.getHistorialUsuario(id)
      .subscribe(historial_usuario=> {
        this.historial_usuario = historial_usuario;
      });
  }

  save(): void {
    if (this.usuario) {
      this.apiService.updateUsuario(this.usuario)
        .subscribe();
    }
  }

}

import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { HistoryComponent } from './history/history.component';
import { authGuard } from './auth.guard';
import { HomeComponent } from './home/home.component';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    {
        path: '',
        component: HomeComponent,
        canActivate: [authGuard],
        children: [
            { path: '', component: HistoryComponent },
            { path: 'users', loadComponent: () => import('./users/users.component').then(m => m.UsersComponent) },
            { path: 'add-user', loadComponent: () => import('./add-user/add-user.component').then(m => m.AddUserComponent) },
            { path: 'users/:id', loadComponent: () => import('./user-detail/user-detail.component').then(m => m.UserDetailComponent) }
        ]
    },

    { path: '**', redirectTo: '' },
];

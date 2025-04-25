export interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    plates: String[];
}

export interface UpdateUser {

    first_name?: string;
    last_name?: string;
    plates?: String[];
}

export interface NewUser {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    plates: String[];
}
export interface UserFormErrorsBase {
    first_name?: string[];
    last_name?: string[];
    email?: string[];
    password?: string[];
    plates?: { [index: number]: string[] };
  }
  
export type NewUser_FormErrors = UserFormErrorsBase;
export type UpdateUser_FormErrors = UserFormErrorsBase;
  

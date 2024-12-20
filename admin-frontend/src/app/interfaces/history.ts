export interface Historial {
    id: number;
    matricula: string;
    fecha: string;     // ISO format (YYYY-MM-DD)
    permitido: boolean;
    usuario_id?: number; 
}
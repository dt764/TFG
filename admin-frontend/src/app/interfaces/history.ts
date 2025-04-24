export interface History {
    id: number;
    plate: string;
    date: string;     // ISO format (YYYY-MM-DD)
    allowed: boolean;
    user_id?: number; 
}
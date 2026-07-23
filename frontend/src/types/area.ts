export type BoundaryPoint = [number, number]; // [lat, lng]

export interface Area {
  id: number;
  name: string;
  boundary: BoundaryPoint[];
  supervisor: number | null;
  supervisor_name: string | null;
  created_at: string;
}

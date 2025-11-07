export enum AuditAction {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  BULK_DELETE = 'bulk_delete',
}

export enum AuditEntity {
  USER = 'user',
  VOUCHER = 'voucher',
}

export interface AuditLog {
  id: string;
  action: AuditAction;
  entity: AuditEntity;
  entityId: number | number[];
  entityName: string;
  performedBy: string;
  performedById: number;
  timestamp: string;
  changes?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface AuditLogFilter {
  action?: AuditAction;
  entity?: AuditEntity;
  performedBy?: string;
  startDate?: string;
  endDate?: string;
}

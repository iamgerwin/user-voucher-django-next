import { AuditLog, AuditAction, AuditEntity, AuditLogFilter } from '@/types/audit-log';

const AUDIT_LOG_KEY = 'audit_logs';
const MAX_LOGS = 1000;

export class AuditLogService {
  private static generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  static createLog(
    action: AuditAction,
    entity: AuditEntity,
    entityId: number | number[],
    entityName: string,
    performedBy: string,
    performedById: number,
    changes?: Record<string, any>,
    metadata?: Record<string, any>
  ): AuditLog {
    const log: AuditLog = {
      id: this.generateId(),
      action,
      entity,
      entityId,
      entityName,
      performedBy,
      performedById,
      timestamp: new Date().toISOString(),
      changes,
      metadata,
    };

    this.saveLogs([log, ...this.getLogs()].slice(0, MAX_LOGS));
    return log;
  }

  static getLogs(): AuditLog[] {
    if (typeof window === 'undefined') return [];

    try {
      const logs = localStorage.getItem(AUDIT_LOG_KEY);
      return logs ? JSON.parse(logs) : [];
    } catch (error) {
      console.error('Failed to retrieve audit logs:', error);
      return [];
    }
  }

  static getFilteredLogs(filter: AuditLogFilter): AuditLog[] {
    let logs = this.getLogs();

    if (filter.action) {
      logs = logs.filter((log) => log.action === filter.action);
    }

    if (filter.entity) {
      logs = logs.filter((log) => log.entity === filter.entity);
    }

    if (filter.performedBy) {
      logs = logs.filter((log) =>
        log.performedBy.toLowerCase().includes(filter.performedBy!.toLowerCase())
      );
    }

    if (filter.startDate) {
      logs = logs.filter((log) => log.timestamp >= filter.startDate!);
    }

    if (filter.endDate) {
      logs = logs.filter((log) => log.timestamp <= filter.endDate!);
    }

    return logs;
  }

  static clearLogs(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(AUDIT_LOG_KEY);
  }

  private static saveLogs(logs: AuditLog[]): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem(AUDIT_LOG_KEY, JSON.stringify(logs));
    } catch (error) {
      console.error('Failed to save audit logs:', error);
    }
  }

  static logUserCreate(userId: number, username: string, performedBy: string, performedById: number): void {
    this.createLog(
      AuditAction.CREATE,
      AuditEntity.USER,
      userId,
      username,
      performedBy,
      performedById
    );
  }

  static logUserUpdate(
    userId: number,
    username: string,
    performedBy: string,
    performedById: number,
    changes: Record<string, any>
  ): void {
    this.createLog(
      AuditAction.UPDATE,
      AuditEntity.USER,
      userId,
      username,
      performedBy,
      performedById,
      changes
    );
  }

  static logUserDelete(userId: number, username: string, performedBy: string, performedById: number): void {
    this.createLog(
      AuditAction.DELETE,
      AuditEntity.USER,
      userId,
      username,
      performedBy,
      performedById
    );
  }

  static logUserBulkDelete(
    userIds: number[],
    performedBy: string,
    performedById: number,
    count: number
  ): void {
    this.createLog(
      AuditAction.BULK_DELETE,
      AuditEntity.USER,
      userIds,
      `${count} users`,
      performedBy,
      performedById,
      undefined,
      { count }
    );
  }

  static logVoucherCreate(
    voucherId: number,
    voucherCode: string,
    performedBy: string,
    performedById: number
  ): void {
    this.createLog(
      AuditAction.CREATE,
      AuditEntity.VOUCHER,
      voucherId,
      voucherCode,
      performedBy,
      performedById
    );
  }

  static logVoucherUpdate(
    voucherId: number,
    voucherCode: string,
    performedBy: string,
    performedById: number,
    changes: Record<string, any>
  ): void {
    this.createLog(
      AuditAction.UPDATE,
      AuditEntity.VOUCHER,
      voucherId,
      voucherCode,
      performedBy,
      performedById,
      changes
    );
  }

  static logVoucherDelete(
    voucherId: number,
    voucherCode: string,
    performedBy: string,
    performedById: number
  ): void {
    this.createLog(
      AuditAction.DELETE,
      AuditEntity.VOUCHER,
      voucherId,
      voucherCode,
      performedBy,
      performedById
    );
  }

  static logVoucherBulkDelete(
    voucherIds: number[],
    performedBy: string,
    performedById: number,
    count: number
  ): void {
    this.createLog(
      AuditAction.BULK_DELETE,
      AuditEntity.VOUCHER,
      voucherIds,
      `${count} vouchers`,
      performedBy,
      performedById,
      undefined,
      { count }
    );
  }
}

export enum ApiEndpoint {
  AUTH_LOGIN = '/auth/login/',
  AUTH_REGISTER = '/auth/register/',
  AUTH_REFRESH = '/auth/refresh/',
  AUTH_LOGOUT = '/auth/logout/',
  USERS = '/users/',
  VOUCHERS = '/vouchers/',
  VOUCHER_USE = '/vouchers/use/',
}

export enum StorageKey {
  ACCESS_TOKEN = 'access_token',
  REFRESH_TOKEN = 'refresh_token',
  USER = 'user',
}

export enum VoucherStatus {
  ACTIVE = 'active',
  USED = 'used',
  EXPIRED = 'expired',
}

export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  PATCH = 'PATCH',
  DELETE = 'DELETE',
}

export enum HttpStatusCode {
  OK = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  INTERNAL_SERVER_ERROR = 500,
}

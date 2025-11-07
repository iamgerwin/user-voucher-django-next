export enum AppRoute {
  HOME = '/',
  LOGIN = '/login',
  REGISTER = '/register',
  DASHBOARD = '/dashboard',
  USERS = '/users',
  USER_NEW = '/users/new',
  USER_DETAIL = '/users',
  VOUCHERS = '/vouchers',
  VOUCHER_NEW = '/vouchers/new',
  VOUCHER_DETAIL = '/vouchers',
}

export const publicRoutes = [
  AppRoute.HOME,
  AppRoute.LOGIN,
  AppRoute.REGISTER,
];

export const authRoutes = [
  AppRoute.LOGIN,
  AppRoute.REGISTER,
];

export const protectedRoutes = [
  AppRoute.DASHBOARD,
  AppRoute.USERS,
  AppRoute.USER_NEW,
  AppRoute.VOUCHERS,
  AppRoute.VOUCHER_NEW,
];

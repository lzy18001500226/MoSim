import type BizError from "./biz";
import type { BizCode } from "./biz";

export type ErrorType = "BIZ" | "DATABASE" | "NETWORK" | "UNKNOWN";

export interface UserFriendlyErrorResponse {
  status: number;
  name: string;
  type: ErrorType;
  code: BizCode;
  message: string;
  // data?: any;
  // stacktrace?: string;
}

export class UserFriendlyError
  extends Error
  implements UserFriendlyErrorResponse
{
  readonly status;
  readonly code;
  readonly type;
  override readonly name;
  override readonly message;
  // readonly data = this.response.data;
  // readonly stacktrace = this.response.stacktrace;

  constructor(private readonly response: UserFriendlyErrorResponse) {
    super(response.message);
    this.status = response.status;
    this.code = response.code;
    this.type = response.type;
    this.message = response.message;
  }

  static fromBiz(biz: BizError) {
    return new UserFriendlyError({
      status: biz.statusCode,
      type: "BIZ",
      name: biz.name,
      code: biz.code,
      message: biz.message,
    });
  }

  // static fromAny(anything: any) {
  //   if (anything instanceof UserFriendlyError) {
  //     return anything;
  //   }

  //   switch (typeof anything) {
  //     case "string":
  //       return UnknownError(anything);
  //     case "object": {
  //       if (anything) {
  //         if (anything instanceof GraphQLError) {
  //           return new UserFriendlyError(anything.extensions);
  //         } else if (anything.type && anything.name && anything.message) {
  //           return new UserFriendlyError(anything);
  //         } else if (anything.message) {
  //           return UnknownError(anything.message);
  //         }
  //       }
  //     }
  //   }

  //   return UnknownError("Unhandled error raised. Please contact us for help.");
  // }

  is(name: BizErrorName) {
    return this.name === name;
  }

  isStatus(status: number) {
    return this.status === status;
  }

  static isNetworkError(error: UserFriendlyError) {
    return error.name === "NETWORK_ERROR";
  }

  static notNetworkError(error: UserFriendlyError) {
    return !UserFriendlyError.isNetworkError(error);
  }

  isNetworkError() {
    return UserFriendlyError.isNetworkError(this);
  }

  notNetworkError() {
    return UserFriendlyError.notNetworkError(this);
  }
}

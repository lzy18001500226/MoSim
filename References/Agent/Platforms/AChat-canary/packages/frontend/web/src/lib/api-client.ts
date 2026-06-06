import { hcWithType } from "@achat/server/hc";

const apiClient = hcWithType("/api", {
  init: {
    credentials: "include",
  },
});
export default apiClient;

// export class BizClientError extends Error {
//   name = "BizError";

//   public readonly code: (typeof BizCodeEnum)[keyof typeof BizCodeEnum];

//   constructor(
//     code: (typeof BizCodeEnum)[keyof typeof BizCodeEnum],
//     message: string
//   ) {
//     super(message);
//     this.code = code;
//   }
// }

// // type RequestFn = (arg: unknown) => Promise<Response>;

// export function fetchWrapper<F extends Function>(fn: F) {
//   return async (
//     args: string | [string | URL, InferRequestType<F>]
//   ): Promise<InferResponseType<F>> => {
//     const res = typeof args === "string" ? await fn() : await fn(args[1]);
//     const data = await res.json();
//     if (!res.ok) {
//       throw new BizClientError(data.code, data.message);
//     }
//     if ("code" in data && "message" in data) {
//       throw new BizClientError(data.code, data.message);
//     }
//     return data as InferResponseType<F>;
//   };
// }
// const useHC = ([endpoint, method]: [Function, MethodKey<Schema>]) => {
//   const res = useSWR(myKey, () => getDuplicateRequestCheck(params), {
//     use: [withIsLoading],
//   });
// };

// export function mutationWrapper<F extends Function>(fn: F) {
//   return async (
//     _url: string | URL,
//     { arg }: { arg: InferRequestType<F> }
//   ): Promise<InferResponseType<F>> => {
//     const res = await fn(arg);
//     const data = await res.json();
//     if (!res.ok) {
//       throw new BizClientError(data.code, data.message);
//     }
//     if (res.status === 204) {
//       return null as InferResponseType<F>;
//     }
//     if ("code" in data && "message" in data) {
//       throw new BizClientError(data.code, data.message);
//     }
//     return data;
//   };
// }

// type ExtractMethod<T> = T extends `$${infer M}`
//   ? M extends "url"
//     ? never
//     : Uppercase<M>
//   : never;
// type MethodKey<S extends Schema> = keyof ClientRequest<S>;

// export function useHC<S extends Schema>(
//   cr: ClientRequest<S>,
//   [method, args]: [
//     ExtractMethod<keyof ClientRequest<S>>,
//     InferRequestType<ClientRequest<S>[MethodKey<S>]>
//   ] = [
//     "GET" as ExtractMethod<keyof ClientRequest<S>>,
//     {} as InferRequestType<ClientRequest<S>[MethodKey<S>]>,
//   ],
//   options?: SWRConfiguration<
//     InferResponseType<ClientRequest<S>[MethodKey<S>]>,
//     Error
//   >
// ) {
//   const prefixedMethod = `$${method.toLowerCase()}` as MethodKey<S>;
//   return useSWR([cr.$url(), args], fetchWrapper(cr[prefixedMethod]), options);
// }

// Desktop counterpart of WasmEnvBundleService. An empty class; the
// `withConnectFallback` proxy in `provider.ts` intercepts every
// `*Connect` method lookup and routes it through the generic
// `connectCall` IPC handler (main fetches the backend Connect endpoint
// directly). Same shape the userCredential service uses.
export class ElectronEnvBundleService {}

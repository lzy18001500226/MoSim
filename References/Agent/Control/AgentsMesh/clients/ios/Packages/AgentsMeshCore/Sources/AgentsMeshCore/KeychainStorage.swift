import Foundation
import Security

/// Keychain-backed `StorageCallback` used by the Rust AuthManager to
/// persist the session token + refresh token between app launches.
///
/// Storage scheme: one generic-password item per key, under the given
/// `service` name (defaults to bundle identifier). The token value is
/// stored as UTF-8 bytes; we don't attempt encryption on top — iOS
/// Keychain already provides hardware-backed protection at the OS level.
public final class KeychainStorage: StorageCallback, @unchecked Sendable {
    private let service: String

    public init(service: String? = nil) {
        self.service = service ?? Bundle.main.bundleIdentifier ?? "agentsmesh.ios"
    }

    public func get(key: String) -> String? {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: key,
            kSecReturnData: true,
            kSecMatchLimit: kSecMatchLimitOne,
        ]
        var out: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &out)
        guard status == errSecSuccess, let data = out as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    public func set(key: String, value: String) {
        let data = Data(value.utf8)
        // Delete-then-add is more reliable than SecItemUpdate for generic
        // passwords: update on a missing item fails, and we've seen
        // attribute-merge edge cases on iOS 16.
        let base: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: key,
        ]
        SecItemDelete(base as CFDictionary)

        var add = base
        add[kSecValueData] = data
        add[kSecAttrAccessible] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        SecItemAdd(add as CFDictionary, nil)
    }

    public func remove(key: String) {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
            kSecAttrAccount: key,
        ]
        SecItemDelete(query as CFDictionary)
    }

    /// Wipe every keychain item under this service. Used by the
    /// `AGENTSMESH_RESET_SESSION=1` debug entry-point so we can boot
    /// from a clean state without uninstalling the app.
    public func clear() {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword,
            kSecAttrService: service,
        ]
        SecItemDelete(query as CFDictionary)
    }
}

# PKI 证书问题排查

## 问题：PKI 服务初始化失败 - x509: invalid ECDSA parameters

### 症状

Backend 启动时出现以下错误，导致 Runner 令牌生成 API 返回 404：

```
Failed to initialize PKI service: failed to parse CA: failed to parse CA certificate: x509: invalid ECDSA parameters
Continuing without gRPC/mTLS support
```

前端表现为"生成 Runner 令牌失败"。

### 原因

使用 `openssl genpkey` 命令生成 ECDSA 私钥时，在某些系统（特别是 macOS）上会生成 PKCS#8 格式的私钥：

```
-----BEGIN PRIVATE KEY-----
MIIBeQIBADCCAQMGByqGSM49AgEwgfcCAQEw...
```

Go 的 `x509.ParsePKCS8PrivateKey()` 对这种格式的 ECDSA 私钥解析可能失败。

### 解决方案

改用 `openssl ecparam` 命令生成传统的 EC 私钥格式：

**错误的命令**（生成 PKCS#8 格式）：
```bash
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:prime256v1 -out ca.key
```

**正确的命令**（生成传统 EC 格式）：
```bash
openssl ecparam -name prime256v1 -genkey -noout -out ca.key
```

正确格式的私钥头部应为：
```
-----BEGIN EC PRIVATE KEY-----
```

### 修复步骤

1. 停止服务：
   ```bash
   docker compose down
   ```

2. 删除旧证书：
   ```bash
   rm -rf ssl/
   ```

3. 重新生成证书（使用修复后的脚本）：
   ```bash
   ./scripts/generate-certs.sh <SERVER_IP>
   ```

4. 验证私钥格式：
   ```bash
   head -1 ssl/ca.key
   # 应输出: -----BEGIN EC PRIVATE KEY-----
   ```

5. 重启服务：
   ```bash
   docker compose up -d
   ```

6. 验证 PKI 初始化成功：
   ```bash
   docker compose logs backend | grep -i pki
   # 应看到: PKI service initialized
   ```

### 验证

PKI 服务正常初始化后，日志中应显示：

```
PKI service initialized
gRPC server configured with mTLS
gRPC/mTLS Runner communication enabled
```

此时 Runner 令牌生成 API 应能正常工作。

### 相关文件

- `deploy/onpremise/scripts/generate-certs.sh` - 证书生成脚本
- `backend/internal/infra/pki/service.go` - PKI 服务实现

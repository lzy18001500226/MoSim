import {
  Body,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Link,
  Preview,
  Tailwind,
  Text,
} from "@react-email/components";

export interface LayoutProps {
  siteName?: string;
  siteLogoUrl?: string;
  siteEmail?: string;
  siteSupportUrl?: string;

  title?: string;
  previewText?: string;
}

export const LayoutPreviewProps = {
  siteName: "Achat",
  siteLogoUrl: "https://achat.dev/logo.svg",
  siteEmail: "support@achat.dev",
  siteSupportUrl: "https://achat.dev",
} satisfies LayoutProps;

const Layout = ({
  siteName,
  siteLogoUrl,
  siteEmail,
  siteSupportUrl,

  title,
  children,
  previewText,
}: LayoutProps & { children: React.ReactNode }) => {
  const preview = previewText ?? title;
  return (
    <Html lang="zh-CN">
      <Head />
      {preview && <Preview>{`[${siteName}] ${preview}`}</Preview>}
      <Tailwind>
        <Body style={main}>
          <Container style={container}>
            <Img src={siteLogoUrl} alt={siteName} height="42" style={logo} />
            {title && <Heading style={h1}>{title}</Heading>}
            {children}
            <Hr style={hr} />
            <Text style={footer}>
              此邮件由系统自动发送，请勿直接回复。
              {siteSupportUrl && (
                <>
                  如需更多帮助，请访问我们的{" "}
                  <Link href={siteSupportUrl} style={link}>
                    帮助中心
                  </Link>
                  。
                </>
              )}
            </Text>
            {siteName && (
              <Text style={footer}>
                &copy; {new Date().getFullYear()} {siteName}. 保留所有权利。
              </Text>
            )}
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

const main = {
  backgroundColor: "#f6f9fc",
  fontFamily:
    '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif',
  padding: "40px 0",
};

const container = {
  backgroundColor: "#ffffff",
  border: "1px solid #eee",
  borderRadius: "5px",
  boxShadow: "0 5px 10px rgba(20, 50, 70, 0.1)",
  margin: "0 auto",
  maxWidth: "600px",
  padding: "20px",
};

const hr = {
  borderColor: "#e5e7eb",
  margin: "30px 0",
};

const logo = {
  margin: "0 auto 20px",
  display: "block",
};

const h1 = {
  color: "#1f2937",
  fontSize: "24px",
  fontWeight: "600",
  lineHeight: "1.4",
  margin: "30px 0",
  padding: "0",
  textAlign: "center" as const,
};

const footer = {
  color: "#6b7280",
  fontSize: "14px",
  lineHeight: "24px",
  textAlign: "center" as const,
  margin: "12px 0",
};

const link = {
  color: "#3b82f6",
  textDecoration: "underline",
};

export default Layout;

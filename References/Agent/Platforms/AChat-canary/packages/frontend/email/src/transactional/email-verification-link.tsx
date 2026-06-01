import {
  Body,
  Button,
  CodeInline,
  Container,
  Head,
  Hr,
  Html,
  Link,
  Preview,
  Section,
  Tailwind,
  Text,
} from "@react-email/components";
import * as React from "react";

interface EmailVerificationEmailProps {
  username?: string;
  inviteLink?: string;
}

export const EmailVerificationEmail = ({
  username,
  inviteLink,
}: EmailVerificationEmailProps) => {
  const previewText = `验证 ${username} 的电子邮箱地址`;

  return (
    <Html>
      <Head />
      <Preview>{previewText}</Preview>
      <Tailwind>
        <Body className="bg-white my-auto mx-auto font-sans px-2">
          <Container className="border border-solid border-[#eaeaea] rounded my-[40px] mx-auto p-[20px] max-w-[465px]">
            <Text className="text-black text-[14px] leading-[24px]">
              尊敬的 <strong>{username}</strong>,
            </Text>
            <Text className="text-black text-[14px] leading-[24px]">
              感谢您选择！
              <br />
              请点击下方按钮或链接激活您的账户！
            </Text>
            <Section className="text-center mt-[32px] mb-[32px]">
              <Button
                className="bg-[#000000] rounded text-white text-[12px] font-semibold no-underline text-center px-5 py-3"
                href={inviteLink}
              >
                激活账户
              </Button>
            </Section>
            <Text className="text-black text-[14px] leading-[24px]">
              或将此 URL 复制并粘贴到浏览器中：
              <Link href={inviteLink} className="text-blue-600 no-underline">
                <CodeInline>{inviteLink}</CodeInline>
              </Link>
            </Text>
            <Hr className="border border-solid border-[#eaeaea] my-[26px] mx-0 w-full" />
            <Text className="text-[#666666] text-[12px] leading-[24px]">
              请勿直接回复此邮件。
              <br />
              如有疑问，请通过 support@nohara.cloud 联系我们。
              <br />
              Nohara 团队敬上
            </Text>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
};

EmailVerificationEmail.PreviewProps = {
  username: "alanturing",
  inviteLink: "https://vercel.com/teams/invite/foo",
} as EmailVerificationEmailProps;

export default EmailVerificationEmail;

import { Section, Text } from "@react-email/components";
import Layout, { type LayoutProps } from "../_components/layout";

interface EmailVerificationCodeProps
  extends Omit<LayoutProps, "children" | "pre"> {
  email: string;
  otp: string;
}

export const EmailVerificationCode = ({
  email,
  otp,
  ...props
}: EmailVerificationCodeProps) => {
  const previewText = `您的验证码是 ${otp}`;

  return (
    <Layout {...props} previewText={previewText}>
      <Text className="text-black text-[14px] leading-[24px]">
        尊敬的 <strong>{email}</strong>,
      </Text>
      <Text className="text-black text-[14px] leading-[24px]">
        您的验证码是
      </Text>
      <Section className="bg-[rgba(0,0,0,0.05)] rounded-md mx-auto my-4 w-[280px] align-middle">
        <Text className="text-black inline-block font-bold text-[32px] tracking-[6px] leading-[40px] py-2 m-0 w-full text-center">
          {otp}
        </Text>
      </Section>
    </Layout>
  );
};

EmailVerificationCode.PreviewProps = {
  email: "alanturing@gmail.com",
  otp: "123456",
} as EmailVerificationCodeProps;

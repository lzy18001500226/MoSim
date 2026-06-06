import { Section, Text } from "@react-email/components";
import { RowButton } from "../_components/button";
import Layout, {
  LayoutPreviewProps,
  type LayoutProps,
} from "../_components/layout";
import { BaseText } from "../_components/text";

interface TicketCreatedEmailProps extends LayoutProps {
  customerName: string;
  ticketNumber: string;
  ticketSubject: string;
  ticketUrl: string;
}

export const TicketCreatedEmail = ({
  ticketNumber,
  customerName,
  ticketSubject,
  ticketUrl,
  ...props
}: TicketCreatedEmailProps) => {
  return (
    <Layout title="工单创建成功" {...props}>
      <BaseText>{customerName}，您好！</BaseText>
      <BaseText>
        感谢您提交工单。您的工单 <strong>{ticketNumber}</strong>{" "}
        已成功创建，我们的客服团队将尽快处理您的请求。
      </BaseText>
      <Section style={ticketInfoSection}>
        <Text style={ticketInfoTitle}>工单详情：</Text>
        <Text style={ticketInfoText}>工单编号：{ticketNumber}</Text>
        <Text style={ticketInfoText}>主题：{ticketSubject}</Text>
        <Text style={ticketInfoText}>状态：等待处理</Text>
      </Section>
      <RowButton href={ticketUrl}>查看工单详情</RowButton>
      <BaseText>我们的客服团队会尽快回复您的工单。</BaseText>
    </Layout>
  );
};

const ticketInfoSection = {
  backgroundColor: "#f9fafb",
  borderRadius: "5px",
  padding: "15px",
  margin: "20px 0",
};

const ticketInfoTitle = {
  color: "#1f2937",
  fontSize: "16px",
  fontWeight: "600",
  margin: "0 0 10px",
};

const ticketInfoText = {
  color: "#4b5563",
  fontSize: "15px",
  margin: "5px 0",
  lineHeight: "1.4",
};

TicketCreatedEmail.PreviewProps = {
  ticketNumber: "TK-12345",
  customerName: "尊敬的客户",
  ticketSubject: "产品使用问题",
  ticketUrl: "https://nohara.cloud/tickets/TK-12345",
  ...LayoutPreviewProps,
} as TicketCreatedEmailProps;

export default TicketCreatedEmail;

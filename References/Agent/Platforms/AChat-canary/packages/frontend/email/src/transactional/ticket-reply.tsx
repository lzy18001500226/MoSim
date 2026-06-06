import { Section, Text } from "@react-email/components";
import { RowButton } from "../_components/button";
import Layout, {
  LayoutPreviewProps,
  type LayoutProps,
} from "../_components/layout";
import { BaseText } from "../_components/text";

interface TicketReplyEmailProps extends LayoutProps {
  ticketNumber: string;
  customerName: string;
  ticketSubject: string;
  replyPreview: string;
  replierName: string;
  ticketUrl: string;
}

export const TicketReplyEmail = ({
  ticketNumber,
  customerName,
  ticketSubject,
  replyPreview,
  replierName,
  ticketUrl,
}: TicketReplyEmailProps) => {
  return (
    <Layout title="您的工单有新回复">
      <BaseText>{customerName}，您好！</BaseText>
      <BaseText>
        您的工单 <strong>{ticketNumber}</strong> 有新的回复。
      </BaseText>
      <Section style={ticketInfoSection}>
        <Text style={ticketInfoTitle}>工单详情：</Text>
        <Text style={ticketInfoText}>工单编号：{ticketNumber}</Text>
        <Text style={ticketInfoText}>主题：{ticketSubject}</Text>
        <Text style={ticketInfoText}>回复人：{replierName}</Text>
      </Section>
      <Section style={replySection}>
        <Text style={replyTitle}>回复内容预览：</Text>
        <Text style={replyContent}>"{replyPreview}"</Text>
      </Section>

      <RowButton href={ticketUrl}>查看完整回复</RowButton>
      <BaseText>
        您可以直接回复此邮件或点击上方按钮查看完整对话并回复。
      </BaseText>
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

const replySection = {
  backgroundColor: "#f0f9ff",
  borderRadius: "5px",
  borderLeft: "4px solid #3b82f6",
  padding: "15px",
  margin: "20px 0",
};

const replyTitle = {
  color: "#1f2937",
  fontSize: "16px",
  fontWeight: "600",
  margin: "0 0 10px",
};

const replyContent = {
  color: "#4b5563",
  fontSize: "15px",
  fontStyle: "italic",
  lineHeight: "1.6",
  margin: "0",
};

TicketReplyEmail.PreviewProps = {
  ticketNumber: "TK-12345",
  customerName: "尊敬的客户",
  ticketSubject: "产品使用问题",
  replyPreview:
    "您好，感谢您联系我们的客服团队。关于您提到的问题，我们建议您...",
  replierName: "客服专员",
  ticketUrl: "https://example.com/tickets/TK-12345",
  ...LayoutPreviewProps,
} as TicketReplyEmailProps;

export default TicketReplyEmail;

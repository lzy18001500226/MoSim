import { Heading, Section, Text } from "@react-email/components";
import { RowButton } from "../_components/button";
import Layout, {
  LayoutPreviewProps,
  type LayoutProps,
} from "../_components/layout";
import { BaseText } from "../_components/text";

interface OrderCancelledEmailProps extends LayoutProps {
  orderNumber: string;
  customerName: string;
  cancellationReason?: string;
  cancellationDate: string;
  refundAmount?: string;
  refundMethod?: string;
}

export const OrderCancelledEmail = ({
  orderNumber = "ORD-12345",
  customerName = "尊敬的客户",
  cancellationReason,
  cancellationDate = "2023年5月23日",
  refundAmount,
  refundMethod,
  ...props
}: OrderCancelledEmailProps) => {
  return (
    <Layout title="您的订单已取消" {...props}>
      <Heading style={h1}>订单已取消</Heading>
      <BaseText>{customerName}，您好！</BaseText>
      <BaseText>
        您的订单 <strong>{orderNumber}</strong> 已于 {cancellationDate} 取消。
      </BaseText>

      <Section style={infoSection}>
        <Text style={infoTitle}>订单详情：</Text>
        <Text style={infoText}>订单编号：{orderNumber}</Text>
        <Text style={infoText}>取消日期：{cancellationDate}</Text>
        {cancellationReason && (
          <Text style={infoText}>取消原因：{cancellationReason}</Text>
        )}
      </Section>

      {refundAmount && (
        <Section style={refundSection}>
          <Text style={refundTitle}>退款信息：</Text>
          <Text style={infoText}>退款金额：{refundAmount}</Text>
          {refundMethod && (
            <Text style={infoText}>退款方式：{refundMethod}</Text>
          )}
          <Text style={infoText}>
            退款将在3-15个工作日内处理完成，具体到账时间取决于您的支付机构。
          </Text>
        </Section>
      )}

      {/* <RowButton href={supportUrl}>联系客服</RowButton> */}

      <BaseText>如果您有任何疑问，请随时联系我们的客服团队。</BaseText>
    </Layout>
  );
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

const infoSection = {
  backgroundColor: "#f9fafb",
  borderRadius: "5px",
  padding: "15px",
  margin: "20px 0",
};

const infoTitle = {
  color: "#1f2937",
  fontSize: "16px",
  fontWeight: "600",
  margin: "0 0 10px",
};

const infoText = {
  color: "#4b5563",
  fontSize: "15px",
  margin: "5px 0",
  lineHeight: "1.4",
};

const refundSection = {
  backgroundColor: "#f0f9ff",
  borderRadius: "5px",
  borderLeft: "4px solid #3b82f6",
  padding: "15px",
  margin: "20px 0",
};

const refundTitle = {
  color: "#1f2937",
  fontSize: "16px",
  fontWeight: "600",
  margin: "0 0 10px",
};

OrderCancelledEmail.PreviewProps = {
  orderNumber: "ORD-12345",
  customerName: "alanturing",
  cancellationReason: "取消原因",
  cancellationDate: "2023年5月23日",
  refundAmount: "100元",
  refundMethod: "支付宝",
  ...LayoutPreviewProps,
};
export default OrderCancelledEmail;

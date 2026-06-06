/** @jsxImportSource react */
import { Section, Text } from "@react-email/components";
import Layout, {
  LayoutPreviewProps,
  type LayoutProps,
} from "../_components/layout";
import { type Order, OrderItem } from "../_components/order";
import { BaseText } from "../_components/text";

interface OrderReceiptProps extends LayoutProps {
  customerName: string;
  order: Order;
}

export const OrderReceiptEmail = ({
  customerName,
  order,
  ...props
}: OrderReceiptProps) => {
  return (
    <Layout title="您的订单收据" {...props}>
      <BaseText>
        尊敬的 <strong>{customerName}</strong>,
      </BaseText>
      <Text className="text-black text-[14px] leading-[24px]">
        感谢您的付款，这是您于
        {order.date.toLocaleDateString("zh-CN", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })}
        的野原云付款收据。
      </Text>
      <OrderItem order={order} paid={true} />
      <Section className="mt-[24px] mb-[24px]">
        <Text className="text-black text-[14px] leading-[24px]">
          {"请您参阅随附的电子发票并保存以备将来参考"}
        </Text>
      </Section>
    </Layout>
  );
};

OrderReceiptEmail.PreviewProps = {
  customerName: "alanturing",
  order: {
    id: "0194f8aa-cada-7d24-bf88-5299a548586b",
    name: "野原云基础版",
    amount: 99,
    method: "支付宝",
    date: new Date("2024-12-25"),
  },
  ...LayoutPreviewProps,
} as OrderReceiptProps;

export default OrderReceiptEmail;

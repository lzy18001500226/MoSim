import { Section, Text } from "@react-email/components";
import Layout, {
  LayoutPreviewProps,
  type LayoutProps,
} from "../_components/layout";
import { type Order, OrderItem } from "../_components/order";
import { BaseText } from "../_components/text";

interface OrderConfirmedProps extends LayoutProps {
  customerName: string;
  order: Order;
}

export const OrderConfirmedEmail = ({
  customerName,
  order,
  ...props
}: OrderConfirmedProps) => {
  return (
    <Layout title="您的订单已被确认" {...props}>
      <BaseText>
        尊敬的 <strong>{customerName}</strong>,
      </BaseText>
      <Text className="text-black text-[14px] leading-[24px]">
        感谢您选择野原云，这是您于
        {order.date.toLocaleDateString("zh-CN", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })}
        的订单确认信息。
      </Text>
      <OrderItem order={order} paid={false} />
      <Section className="mt-[24px] mb-[24px]">
        <Text className="text-black text-[14px] leading-[24px]">
          {"请您尽快完成支付以确保订单生效。未支付的订单将在30分钟内自动取消。"}
        </Text>
      </Section>
    </Layout>
  );
};

OrderConfirmedEmail.PreviewProps = {
  customerName: "alanturing",
  order: {
    id: "0194f8aa-cada-7d24-bf88-5299a548586b",
    name: "野原云基础版",
    amount: 99,
    method: "支付宝",
    date: new Date("2024-12-25"),
  },
  ...LayoutPreviewProps,
} as OrderConfirmedProps;

export default OrderConfirmedEmail;

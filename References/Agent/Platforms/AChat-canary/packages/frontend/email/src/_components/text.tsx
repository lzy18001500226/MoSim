import { Text } from "@react-email/components";

export const BaseText = ({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) => {
  return <Text style={{ ...text, ...style }}>{children}</Text>;
};

const text = {
  color: "#4b5563",
  fontSize: "16px",
  lineHeight: "1.6",
  margin: "16px 0",
};

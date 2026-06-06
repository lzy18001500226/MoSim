import { Button  Section } from "@react-email/components";

export const RowButton = ({
  href,
  children,
}: { href: string; children: React.ReactNode }) => {
  return (
    <Section style={buttonContainer}>
      <Button style={button} href={href}>
        {children}
      </Button>
    </Section>
  );
};

const buttonContainer = {
  textAlign: "center" as const,
  margin: "30px 0",
};

const button = {
  padding: "10px 20px",
  backgroundColor: "#3b82f6",
  borderRadius: "5px",
  color: "#fff",
  display: "inline-block",
  fontSize: "16px",
  fontWeight: "600",
  textDecoration: "none",
  textAlign: "center" as const,
  width: "auto",
};

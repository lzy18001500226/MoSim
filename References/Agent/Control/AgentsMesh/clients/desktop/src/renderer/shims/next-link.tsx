import React from "react";
import { Link as RouterLink, type LinkProps as RouterLinkProps } from "react-router-dom";

export interface LinkProps
  extends Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, "href">,
    Pick<RouterLinkProps, "replace" | "state"> {
  href: string;
  prefetch?: boolean;
  scroll?: boolean;
}

const Link = React.forwardRef<HTMLAnchorElement, LinkProps>(
  ({ href, prefetch: _, scroll: __, children, ...props }, ref) => {
    if (href.startsWith("http://") || href.startsWith("https://") || href.startsWith("mailto:")) {
      return (
        <a ref={ref} href={href} {...props}>
          {children}
        </a>
      );
    }

    return (
      <RouterLink ref={ref} to={href} {...props}>
        {children}
      </RouterLink>
    );
  },
);

Link.displayName = "Link";
export default Link;

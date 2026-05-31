// Shared label and variant constants for support ticket display

export const statusLabels: Record<string, string> = {
  open: "Open",
  in_progress: "In Progress",
  resolved: "Resolved",
  closed: "Closed",
};

export const statusVariants: Record<string, "default" | "secondary" | "destructive" | "outline" | "success" | "warning"> = {
  open: "destructive",
  in_progress: "warning",
  resolved: "success",
  closed: "secondary",
};

export const categoryLabels: Record<string, string> = {
  bug: "Bug",
  feature_request: "Feature Request",
  usage_question: "Usage Question",
  account: "Account",
  other: "Other",
};

export const categoryVariants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  bug: "destructive",
  feature_request: "default",
  usage_question: "secondary",
  account: "outline",
  other: "secondary",
};

export const priorityLabels: Record<string, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export const priorityVariants: Record<string, "default" | "secondary" | "destructive" | "outline" | "warning"> = {
  low: "secondary",
  medium: "warning",
  high: "destructive",
};

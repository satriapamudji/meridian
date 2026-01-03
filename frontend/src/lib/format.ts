export const formatDateTime = (value: string | null) => {
  if (!value) {
    return "Unscheduled";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(parsed);
};

export const formatStatus = (value: string | null) => {
  if (!value) {
    return "pending";
  }
  return value.replace(/_/g, " ");
};

export const formatScoreBand = (score: number) => {
  if (score >= 65) {
    return "Priority";
  }
  if (score >= 50) {
    return "Monitoring";
  }
  return "Logged";
};

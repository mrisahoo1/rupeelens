export const categories = [
  "Food & Dining", "Groceries", "Transport", "Fuel", "Shopping", "Entertainment", "Travel", "Rent & Housing", "Utilities", "Mobile & Internet", "Health & Pharmacy", "Fitness", "Education", "Subscriptions", "Insurance", "Investments", "Credit Card Payment", "Bank Transfer", "UPI Transfer", "Fees & Charges", "Cash Withdrawal", "Gifts & Family", "Personal Care", "Electronics", "Home", "Miscellaneous", "Uncategorized"
] as const;
export type Category = typeof categories[number];

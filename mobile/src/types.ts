export type PetCareUser = {
  id: number;
  username: string;
  display_name: string;
  role: string;
  role_label: string;
  must_change_password: boolean;
};

export type PetCareSession = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: PetCareUser;
  permissions: string[];
};

export type RpcDraft = {
  requestId: string;
  userId: number;
  title: string;
  method: string;
  args: unknown[];
  createdAt: string;
  status: 'queued' | 'needs-review';
  error?: string;
  result?: unknown;
};

export type RpcRequestStatus = {
  request_id: string;
  status: 'RUNNING' | 'SUCCEEDED' | 'FAILED';
  result: unknown;
  error_status: number | null;
  error_message: string | null;
};

export type StorefrontItem = {
  id: string;
  item_code: string;
  name: string;
  category?: string;
  catalog_category?: string;
  description?: string;
  retail_price: number;
  promotion_percent?: number;
  is_demo: boolean | number;
  usable_quantity: number;
  type: string;
};

export type StorefrontCatalog = {
  products: StorefrontItem[];
  combos: StorefrontItem[];
};

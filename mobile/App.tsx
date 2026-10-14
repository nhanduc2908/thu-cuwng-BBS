import NetInfo, { type NetInfoState } from '@react-native-community/netinfo';
import { StatusBar } from 'expo-status-bar';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ActionButton, EmptyState, Field, ScreenHeader, Surface } from './src/components';
import { ApiError, createRequestId, PetCareApi } from './src/api';
import { ActionForm, type MobileFormField } from './src/action-form';
import { CustomerStorefront } from './src/customer-storefront';
import {
  clearSession,
  getSavedApiUrl,
  loadSession,
  readDrafts,
  saveApiUrl,
  writeDrafts,
} from './src/storage';
import { colors, spacing } from './src/theme';
import type { PetCareSession, RpcDraft } from './src/types';

type TabKey =
  | 'dashboard'
  | 'animals'
  | 'customers'
  | 'sales'
  | 'inventory'
  | 'imports'
  | 'store'
  | 'care'
  | 'health'
  | 'services'
  | 'memberships'
  | 'reports'
  | 'team'
  | 'notifications'
  | 'audit'
  | 'approvals';
type DataSet = Record<string, unknown>;
type FormDefinition = {
  title: string;
  description?: string;
  fields: MobileFormField[];
  submitLabel: string;
  onSubmit: (values: Record<string, string>) => void;
};

const TABS: {
  key: TabKey;
  label: string;
  permission: string;
}[] = [
  { key: 'dashboard', label: 'Tổng quan', permission: 'dashboard.view' },
  { key: 'animals', label: 'Thú cưng', permission: 'animals.view' },
  { key: 'customers', label: 'Khách hàng', permission: 'sales.view' },
  { key: 'sales', label: 'Bán hàng', permission: 'sales.view' },
  { key: 'inventory', label: 'Kho', permission: 'inventory.view' },
  { key: 'imports', label: 'Nhập hàng', permission: 'imports.view' },
  { key: 'store', label: 'Chuồng trại', permission: 'store.view' },
  { key: 'care', label: 'Chăm sóc', permission: 'care.view' },
  { key: 'health', label: 'Sức khỏe', permission: 'health.view' },
  { key: 'services', label: 'Dịch vụ', permission: 'services.view' },
  { key: 'memberships', label: 'Hội viên', permission: 'membership.view' },
  { key: 'reports', label: 'Báo cáo', permission: 'reports.view' },
  { key: 'team', label: 'Nhân sự', permission: 'users.manage' },
  { key: 'notifications', label: 'Thông báo', permission: 'notifications.view' },
  { key: 'audit', label: 'Nhật ký', permission: 'audit.view' },
  { key: 'approvals', label: 'Duyệt', permission: 'sales.approve' },
];

export default function App() {
  const [apiUrl, setApiUrl] = useState('');
  const [customerMode, setCustomerMode] = useState(false);
  const [api, setApi] = useState<PetCareApi | null>(null);
  const [booting, setBooting] = useState(true);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<TabKey>('dashboard');
  const [data, setData] = useState<DataSet>({});
  const [loadingData, setLoadingData] = useState(false);
  const [activeForm, setActiveForm] = useState<FormDefinition | null>(null);
  const [fromCache, setFromCache] = useState(false);
  const [drafts, setDrafts] = useState<RpcDraft[]>([]);
  const [draftsLoaded, setDraftsLoaded] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Record<string, unknown> | null>(null);
  const [selectedAnimal, setSelectedAnimal] = useState<Record<string, unknown> | null>(null);
  const syncLock = useRef(false);

  useEffect(() => {
    let active = true;
    const unsubscribe = NetInfo.addEventListener((state: NetInfoState) => {
      if (active) setConnected(Boolean(state.isConnected && state.isInternetReachable !== false));
    });
    NetInfo.fetch()
      .then((state) => {
        if (active) setConnected(Boolean(state.isConnected && state.isInternetReachable !== false));
      })
      .catch((reason: unknown) => {
        if (active) setError(errorMessage(reason));
      });
    Promise.all([getSavedApiUrl(), loadSession()])
      .then(async ([savedUrl, session]) => {
        if (!active) return;
        setApiUrl(savedUrl);
        if (savedUrl && session) {
          setApi(await PetCareApi.resume(savedUrl, session));
        }
      })
      .catch((reason: unknown) => {
        if (active) setError(errorMessage(reason));
      })
      .finally(() => {
        if (active) setBooting(false);
      });
    return () => {
      active = false;
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (!api) {
      setDrafts([]);
      setDraftsLoaded(false);
      return;
    }
    let active = true;
    setDraftsLoaded(false);
    readDrafts(api.user.id)
      .then((savedDrafts) => {
        if (active) {
          setDrafts(savedDrafts);
          setDraftsLoaded(true);
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(errorMessage(reason));
          setDraftsLoaded(true);
        }
      });
    return () => {
      active = false;
    };
  }, [api]);

  useEffect(() => {
    if (!api || !draftsLoaded) return;
    writeDrafts(api.user.id, drafts).catch((reason: unknown) => {
      setError(`Không thể lưu hàng đợi ngoại tuyến: ${errorMessage(reason)}`);
    });
  }, [api, drafts, draftsLoaded]);

  const availableTabs = useMemo(
    () => TABS.filter((item) => {
      return api?.can(item.permission);
    }),
    [api],
  );

  useEffect(() => {
    if (availableTabs.length > 0 && !availableTabs.some((item) => item.key === tab)) {
      setTab(availableTabs[0].key);
    }
  }, [availableTabs, tab]);

  const loadTab = useCallback(async () => {
    if (!api || api.user.must_change_password) return;
    setLoadingData(true);
    setError('');
    try {
      let next: DataSet = {};
      let usedCache = false;
      const read = async <T,>(key: string, method: string, args: unknown[] = []) => {
        const response = await api.read<T>(method, args, `${tab}:${key}`);
        usedCache ||= response.fromCache;
        return response.data;
      };
      if (tab === 'dashboard') {
        const [counts, recent, alerts] = await Promise.all([
          read<unknown>('counts', 'dashboard_counts'),
          read<unknown>('recent-animals', 'recent_animals', [5]),
          api.can('notifications.view')
            ? read<unknown>('alerts', 'list_operational_alerts')
            : Promise.resolve([]),
        ]);
        next = { counts, recent, alerts };
      } else if (tab === 'animals') {
        next = { animals: await read('animals', 'list_animals') };
      } else if (tab === 'customers') {
        next = { customers: await read('customers', 'list_customers') };
      } else if (tab === 'sales' || tab === 'approvals') {
        const requests = [
          read('orders', 'list_sales_orders'),
          read('reservations', 'list_reservations'),
          read('approval-requests', 'list_sales_approval_requests'),
        ];
        if (tab === 'sales') {
          requests.push(read('customers', 'list_customers'));
          requests.push(read('saleable-animals', 'list_saleable_animals'));
        }
        const result = await Promise.all(requests);
        next = {
          orders: result[0],
          reservations: result[1],
          approvals: result[2],
          customers: result[3] ?? [],
          saleableAnimals: result[4] ?? [],
        };
      } else if (tab === 'inventory') {
        const [items, alerts] = await Promise.all([
          read('inventory', 'list_inventory_items'),
          read('low-stock', 'low_stock_items'),
        ]);
        next = { items, alerts };
      } else if (tab === 'imports') {
        const [suppliers, batches] = await Promise.all([
          read('suppliers', 'list_suppliers'),
          read('import-batches', 'list_import_batches'),
        ]);
        next = { suppliers, batches };
      } else if (tab === 'store') {
        const [cages, animals] = await Promise.all([
          read('cages', 'list_cages'),
          api.can('animals.view') ? read('animals', 'list_animals') : Promise.resolve([]),
        ]);
        next = { cages, animals };
      } else if (tab === 'care') {
        const [tasks, animals] = await Promise.all([
          read('care-tasks', 'list_care_tasks'),
          api.can('animals.view') ? read('animals', 'list_animals') : Promise.resolve([]),
        ]);
        next = { tasks, animals };
      } else if (tab === 'health') {
        const [health, vaccination, animals] = await Promise.all([
          read('health-records', 'list_health_records'),
          api.can('animals.view')
            ? read('vaccination-schedules', 'list_vaccination_schedules')
            : Promise.resolve([]),
          api.can('animals.view') ? read('animals', 'list_animals') : Promise.resolve([]),
        ]);
        next = { health, vaccination, animals };
      } else if (tab === 'services') {
        const [appointments, packages, customers] = await Promise.all([
          read('service-appointments', 'list_service_appointments'),
          read('service-packages', 'list_service_packages'),
          api.can('sales.view') ? read('customers', 'list_customers') : Promise.resolve([]),
        ]);
        next = { appointments, packages, customers };
      } else if (tab === 'memberships') {
        const [memberships, plans, bills, customers] = await Promise.all([
          read('memberships', 'list_memberships'),
          read('membership-plans', 'list_membership_plans'),
          read('membership-bills', 'list_membership_bills'),
          api.can('sales.view') ? read('customers', 'list_customers') : Promise.resolve([]),
        ]);
        next = { memberships, plans, bills, customers };
      } else if (tab === 'reports') {
        const today = new Date();
        const firstDay = localDateString(
          new Date(today.getFullYear(), today.getMonth(), 1),
        );
        const lastDay = localDateString(today);
        const [sales, inventory, health] = await Promise.all([
          read('sales-report', 'report_sales', [firstDay, lastDay]),
          read('inventory-report', 'report_inventory'),
          read('health-report', 'report_health', [firstDay, lastDay]),
        ]);
        next = { sales, inventory, health };
      } else if (tab === 'team') {
        const [users, count] = await Promise.all([
          read('users', 'list_users'),
          read('user-count', 'user_count'),
        ]);
        next = { users, userCount: count };
      } else if (tab === 'notifications') {
        next = { alerts: await read('operational-alerts', 'list_operational_alerts') };
      } else if (tab === 'audit') {
        next = { events: await read('audit-events', 'list_audit_events') };
      }
      setData(next);
      setFromCache(usedCache);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) {
        setApi(null);
        setData({});
        return;
      }
      setError(errorMessage(reason));
    } finally {
      setLoadingData(false);
    }
  }, [api, tab]);

  useEffect(() => {
    void loadTab();
  }, [loadTab]);

  const updateDraft = useCallback((requestId: string, update: Partial<RpcDraft>) => {
    setDrafts((current) =>
      current.map((draft) =>
        draft.requestId === requestId ? { ...draft, ...update } : draft,
      ),
    );
  }, []);

  const queueRpc = useCallback((title: string, method: string, args: unknown[]) => {
    if (!api || !draftsLoaded) {
      setError('Hàng đợi chưa sẵn sàng. Vui lòng thử lại.');
      return;
    }
    const draft: RpcDraft = {
      requestId: createRequestId(),
      userId: api.user.id,
      title,
      method,
      args,
      createdAt: new Date().toISOString(),
      status: 'queued',
    };
    setDrafts((current) => [draft, ...current]);
    setActiveForm(null);
    setError('');
  }, [api, draftsLoaded]);

  const openForm = useCallback((definition: FormDefinition) => {
    setActiveForm(definition);
  }, []);

  const openProductSaleForm = useCallback(() => {
    if (!api) return;
    const customers = asRows(data.customers);
    const customerOptions = mobileRecordOptions(customers, 'customer_code');
    if (customerOptions.length === 0) {
      setError('Cần có hồ sơ khách hàng trước khi tạo đơn bán sản phẩm.');
      return;
    }
    openForm({
      title: 'Tạo đơn bán sản phẩm / combo',
      description: 'Chọn khách hàng để tải giá bán và tồn kho mới nhất từ máy chủ.',
      submitLabel: 'Tiếp tục',
      fields: [
        { key: 'customer', label: 'Khách hàng', required: true, options: customerOptions },
      ],
      onSubmit: async (values) => {
        const customerId = optionId(values.customer);
        try {
          const [productsResult, combosResult] = await Promise.all([
            api.read<unknown[]>('list_saleable_products', [customerId], `sales:products:${customerId}`),
            api.read<unknown[]>('list_saleable_combos', [customerId], `sales:combos:${customerId}`),
          ]);
          const products = asRows(productsResult.data)
            .filter((row) => Number(row.available) > 0)
            .map((row) => ({
              option: `SKU · ${text(row.item_code) || text(row.id)} · ${displayName(row)} · còn ${text(row.available)} · ${formatMoney(row.sale_price)}`,
              id: Number(row.id),
              maximum: Number(row.available),
            }))
            .filter((choice) =>
              Number.isInteger(choice.id) && choice.id > 0 &&
              Number.isFinite(choice.maximum) && choice.maximum > 0,
            );
          const combos = asRows(combosResult.data)
            .filter((row) => Boolean(row.available))
            .map((row) => ({
              option: `Combo · ${text(row.combo_code) || text(row.id)} · ${displayName(row)} · ${formatMoney(row.sale_price)}`,
              id: Number(row.id),
              maximum: Number(row.max_quantity),
            }))
            .filter((choice) =>
              Number.isInteger(choice.id) && choice.id > 0 &&
              Number.isFinite(choice.maximum) && choice.maximum > 0,
            );
          if (products.length === 0 && combos.length === 0) {
            setActiveForm(null);
            setError('Khách hàng này hiện chưa có sản phẩm hoặc combo đủ tồn để bán.');
            return;
          }
          const orderCode = `MOB-${localDateString(new Date()).replaceAll('-', '')}-${createRequestId().slice(-8).toUpperCase()}`;
          openForm({
            title: 'Chi tiết đơn bán',
            description: 'Có thể chọn một SKU, một combo hoặc cả hai. Giá, tồn kho và quyền duyệt được máy chủ kiểm tra khi đồng bộ.',
            submitLabel: 'Gửi đơn',
            fields: [
              { key: 'order_code', label: 'Mã đơn hàng', initialValue: orderCode, required: true },
              ...(products.length > 0 ? [
                { key: 'product', label: 'Sản phẩm (SKU)', options: products.map((choice) => choice.option) },
                { key: 'product_quantity', label: 'Số lượng sản phẩm', initialValue: '1', keyboardType: 'decimal-pad' as const },
              ] : []),
              ...(combos.length > 0 ? [
                { key: 'combo', label: 'Combo', options: combos.map((choice) => choice.option) },
                { key: 'combo_quantity', label: 'Số lượng combo', initialValue: '1', keyboardType: 'decimal-pad' as const },
              ] : []),
              { key: 'note', label: 'Ghi chú' },
            ],
            onSubmit: (orderValues) => {
              const selectedProduct = products.find((choice) => choice.option === orderValues.product);
              const selectedCombo = combos.find((choice) => choice.option === orderValues.combo);
              if (!selectedProduct && !selectedCombo) {
                setError('Hãy chọn ít nhất một sản phẩm hoặc combo.');
                return;
              }
              const productQuantity = Number(orderValues.product_quantity);
              const comboQuantity = Number(orderValues.combo_quantity);
              if (
                (selectedProduct && (!Number.isFinite(productQuantity) || productQuantity <= 0)) ||
                (selectedCombo && (!Number.isFinite(comboQuantity) || comboQuantity <= 0)) ||
                (selectedProduct && productQuantity > selectedProduct.maximum) ||
                (selectedCombo && comboQuantity > selectedCombo.maximum)
              ) {
                setError('Số lượng phải lớn hơn 0 và không vượt quá tồn kho khả dụng.');
                return;
              }
              const values = {
                order_code: orderValues.order_code.trim(),
                customer_id: customerId,
                ordered_at: localDateString(new Date()),
                note: orderValues.note.trim(),
                product_lines: selectedProduct
                  ? [{ item_id: selectedProduct.id, quantity: productQuantity }]
                  : [],
                combo_lines: selectedCombo
                  ? [{ combo_id: selectedCombo.id, quantity: comboQuantity }]
                  : [],
              };
              queueRpc('Tạo đơn bán sản phẩm / combo', 'submit_sales_action', [
                'create_product_sales_order',
                { values },
              ]);
            },
          });
        } catch (reason) {
          setActiveForm(null);
          setError(`Không thể tải catalog bán hàng: ${errorMessage(reason)}`);
        }
      },
    });
  }, [api, data.customers, openForm, queueRpc]);

  const openPaymentForm = useCallback((order: Record<string, unknown>) => {
    const orderId = Number(order.id);
    const balance = Number(order.total_amount) - Number(order.paid_amount ?? 0);
    if (!Number.isInteger(orderId) || orderId < 1 || !Number.isFinite(balance) || balance <= 0) {
      setError('Không thể xác định công nợ còn lại của đơn hàng.');
      return;
    }
    openForm({
      title: `Ghi nhận thanh toán ${text(order.order_code)}`,
      submitLabel: 'Gửi thanh toán',
      fields: [
        { key: 'amount', label: 'Số tiền (VND)', initialValue: String(balance), keyboardType: 'decimal-pad', required: true },
        { key: 'method', label: 'Phương thức', required: true, options: ['CASH', 'BANK_TRANSFER', 'CARD', 'OTHER'] },
        { key: 'reference', label: 'Mã giao dịch' },
        { key: 'note', label: 'Ghi chú' },
      ],
      onSubmit: (values) => {
        const amount = Number(values.amount);
        if (!Number.isFinite(amount) || amount <= 0 || amount > balance) {
          setError(`Số tiền phải lớn hơn 0 và không vượt quá ${formatMoney(balance)}.`);
          return;
        }
        queueRpc('Ghi nhận thanh toán đơn hàng', 'submit_sales_action', [
          'add_payment',
          {
            order_id: orderId,
            values: {
              amount,
              method: values.method,
              paid_at: localDateString(new Date()),
              reference: values.reference.trim(),
              note: values.note.trim(),
            },
          },
        ]);
      },
    });
  }, [openForm, queueRpc]);

  const syncOutbox = useCallback(async () => {
    if (
      !api ||
      !connected ||
      !draftsLoaded ||
      syncLock.current ||
      api.user.must_change_password
    ) return;
    syncLock.current = true;
    try {
      try {
        await writeDrafts(api.user.id, drafts);
      } catch (reason) {
        setError(`Không thể lưu yêu cầu trước khi đồng bộ: ${errorMessage(reason)}`);
        return;
      }
      const pending = drafts.filter((draft) => draft.status === 'queued');
      for (const draft of pending) {
        try {
          let result: unknown;
          try {
            const status = await api.getRequestStatus(draft.requestId);
            if (status.status === 'RUNNING') {
              updateDraft(draft.requestId, {
                status: 'needs-review',
                error: 'Yêu cầu đang được máy chủ xử lý. Hãy kiểm tra lại sau.',
              });
              continue;
            }
            if (status.status === 'FAILED') {
              updateDraft(draft.requestId, {
                status: 'needs-review',
                error: status.error_message ?? 'Máy chủ báo thao tác thất bại.',
              });
              continue;
            }
            result = status.result;
          } catch (reason) {
            if (
              !(reason instanceof ApiError) ||
              reason.status !== 404 ||
              reason.message !== 'Request not found.'
            ) {
              throw reason;
            }
            result = await api.rpc(draft.method, draft.args, draft.requestId);
          }
          setDrafts((current) =>
            current.filter((item) => item.requestId !== draft.requestId),
          );
          setError('');
          Alert.alert(
            'Đã đồng bộ yêu cầu',
            `${draft.title}\n${describeResult(result)}`,
          );
          void loadTab();
        } catch (reason) {
          const message = errorMessage(reason);
          updateDraft(draft.requestId, { status: 'needs-review', error: message });
          if (reason instanceof ApiError && reason.status === 401) {
            setApi(null);
            break;
          }
          if (!(reason instanceof ApiError) || reason.status === undefined) break;
        }
      }
    } finally {
      syncLock.current = false;
    }
  }, [api, connected, drafts, draftsLoaded, loadTab, updateDraft]);

  useEffect(() => {
    void syncOutbox();
  }, [syncOutbox]);

  const signIn = async () => {
    setBusy(true);
    setError('');
    try {
      await saveApiUrl(apiUrl);
      const signedIn = await PetCareApi.signIn(apiUrl, username, password);
      setApiUrl(signedIn.baseUrl);
      setApi(signedIn);
      setPassword('');
      setData({});
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy(false);
    }
  };

  const changePassword = async () => {
    if (newPassword !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      await api?.changePassword(currentPassword, newPassword);
      await api?.refreshProfile();
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      await loadTab();
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy(false);
    }
  };

  const signOut = async () => {
    if (!api) return;
    setBusy(true);
    try {
      await api.signOut();
      await clearSession();
      setApi(null);
      setData({});
      setDrafts([]);
      setError('');
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setBusy(false);
    }
  };

  const queueReservation = async () => {
    if (!selectedCustomer || !selectedAnimal) {
      setError('Hãy chọn khách hàng và thú cưng cần giữ chỗ.');
      return;
    }
    const now = new Date();
    const requestId = createRequestId();
    const values = {
      customer_id: Number(selectedCustomer.id),
      animal_id: Number(selectedAnimal.id),
      reserved_at: localDateString(now),
      expires_at: localDateString(new Date(now.getTime() + 24 * 60 * 60 * 1000)),
      deposit: 0,
      note: 'Yêu cầu tạo từ ứng dụng PetCare Mobile',
    };
    const draft: RpcDraft = {
      requestId,
      userId: api?.user.id ?? 0,
      title: `Giữ chỗ ${displayName(selectedAnimal)}`,
      method: 'submit_sales_action',
      args: ['create_reservation', { values }],
      createdAt: now.toISOString(),
      status: 'queued',
    };
    setDrafts((current) => [draft, ...current]);
    setSelectedCustomer(null);
    setSelectedAnimal(null);
    setError('');
  };

  const queueReview = (row: Record<string, unknown>, approve: boolean) => {
    const requestId = Number(row.id);
    if (!Number.isInteger(requestId) || requestId < 1) {
      setError('Mã yêu cầu duyệt không hợp lệ.');
      return;
    }
    const title = `${approve ? 'Duyệt' : 'Từ chối'} ${text(row.request_code) || `yêu cầu #${requestId}`}`;
    Alert.alert(
      approve ? 'Xác nhận duyệt' : 'Xác nhận từ chối',
      `${title}? Thao tác sẽ được gửi lên hệ thống và không thể tự hoàn tác.`,
      [
        { text: 'Hủy', style: 'cancel' },
        {
          text: approve ? 'Duyệt yêu cầu' : 'Từ chối yêu cầu',
          style: approve ? 'default' : 'destructive',
          onPress: () => {
            const draft: RpcDraft = {
              requestId: createRequestId(),
              userId: api?.user.id ?? 0,
              title,
              method: 'review_sales_approval_request',
              args: [requestId, approve, 'Đã xem xét qua ứng dụng PetCare Mobile'],
              createdAt: new Date().toISOString(),
              status: 'queued',
            };
            setDrafts((current) => [draft, ...current]);
          },
        },
      ],
    );
  };

  const retryDraft = (draft: RpcDraft) => {
    updateDraft(draft.requestId, { status: 'queued', error: undefined });
  };
  const dismissDraft = (draft: RpcDraft) => {
    setDrafts((current) =>
      current.filter((item) => item.requestId !== draft.requestId),
    );
  };

  if (booting) {
    return <LoadingScreen label="Đang khởi động PetCare..." />;
  }

  if (!api) {
    if (customerMode) {
      return (
        <CustomerStorefront
          apiUrl={apiUrl}
          onApiUrl={setApiUrl}
          onBack={() => {
            setCustomerMode(false);
            setError('');
          }}
        />
      );
    }
    return (
      <AuthScreen
        apiUrl={apiUrl}
        busy={busy}
        error={error}
        onApiUrl={setApiUrl}
        onPassword={setPassword}
        onSignIn={signIn}
        onCustomerStore={() => {
          setCustomerMode(true);
          setError('');
        }}
        onUsername={setUsername}
        password={password}
        username={username}
      />
    );
  }

  if (api.user.must_change_password) {
    return (
      <PasswordScreen
        busy={busy}
        currentPassword={currentPassword}
        error={error}
        newPassword={newPassword}
        onChange={changePassword}
        onCurrentPassword={setCurrentPassword}
        onNewPassword={setNewPassword}
        onSignOut={signOut}
        onConfirmPassword={setConfirmPassword}
        confirmPassword={confirmPassword}
      />
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View style={styles.appHeader}>
        <View style={styles.brandMark}><Text style={styles.brandMarkText}>P</Text></View>
        <View style={styles.brandCopy}>
          <Text style={styles.brandName}>PetCare</Text>
          <Text style={styles.brandUser}>{api.user.display_name} · {api.user.role_label}</Text>
        </View>
        <Pressable
          accessibilityRole="button"
          onPress={() => Alert.alert('Đăng xuất', 'Bạn muốn kết thúc phiên làm việc?', [
            { text: 'Ở lại', style: 'cancel' },
            { text: 'Đăng xuất', style: 'destructive', onPress: () => void signOut() },
          ])}
          style={styles.signOutButton}
        >
          <Text style={styles.signOutText}>Thoát</Text>
        </Pressable>
      </View>
      <View style={styles.connectionBar}>
        <View style={[styles.connectionDot, connected ? styles.onlineDot : styles.offlineDot]} />
        <Text style={styles.connectionText}>
          {connected ? 'Đang kết nối máy chủ' : 'Ngoại tuyến · hiển thị dữ liệu đã lưu'}
        </Text>
        {drafts.length > 0 ? <Text style={styles.outboxCount}>{drafts.length} chờ đồng bộ</Text> : null}
      </View>
      {availableTabs.length > 0 ? (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.tabs}
        >
          {availableTabs.map((item) => (
            <Pressable
              accessibilityRole="tab"
              accessibilityState={{ selected: tab === item.key }}
              key={item.key}
              onPress={() => setTab(item.key)}
              style={[styles.tab, tab === item.key && styles.activeTab]}
            >
              <Text style={[styles.tabText, tab === item.key && styles.activeTabText]}>{item.label}</Text>
            </Pressable>
          ))}
        </ScrollView>
      ) : (
        <View style={styles.content}><EmptyState title="Tài khoản chưa được cấp khu vực sử dụng" detail="Liên hệ quản trị viên để được phân quyền." /></View>
      )}
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
        refreshControl={undefined}
      >
        {error ? <ErrorBanner message={error} onDismiss={() => setError('')} /> : null}
        {fromCache ? <Text style={styles.cacheNotice}>Đang xem bản lưu gần nhất trên thiết bị.</Text> : null}
        {tab === 'dashboard' ? <DashboardView data={data} loading={loadingData} onRefresh={() => void loadTab()} /> : null}
        {tab === 'animals' ? (
          <>
            {api.can('animals.manage') ? (
              <ActionButton
                label="Thêm hồ sơ thú cưng"
                onPress={() => openForm({
                  title: 'Thêm thú cưng',
                  submitLabel: 'Lưu hồ sơ',
                  fields: [
                    { key: 'animal_code', label: 'Mã thú cưng', required: true },
                    { key: 'name', label: 'Tên thú cưng', required: true },
                    { key: 'species', label: 'Loài', required: true, options: ['Chó', 'Mèo', 'Thỏ', 'Chim', 'Cá', 'Bò sát'] },
                    { key: 'breed', label: 'Giống' },
                    { key: 'gender', label: 'Giới tính', initialValue: 'Chưa rõ', options: ['Đực', 'Cái', 'Chưa rõ'] },
                    { key: 'sale_price', label: 'Giá bán (VND)', keyboardType: 'numeric' },
                    { key: 'status', label: 'Trạng thái', initialValue: 'PENDING_INSPECTION', options: ['PENDING_INSPECTION', 'AVAILABLE', 'QUARANTINE'] },
                    { key: 'description', label: 'Ghi chú' },
                  ],
                  onSubmit: (values) => queueRpc('Thêm hồ sơ thú cưng', 'save_animal', [{
                    ...values,
                    sale_price: Number(values.sale_price || 0),
                  }]),
                })}
              />
            ) : null}
            <ListView title="Thú cưng" rows={asRows(data.animals)} loading={loadingData} empty="Chưa có dữ liệu thú cưng." />
          </>
        ) : null}
        {tab === 'customers' ? (
          <>
            {api.can('sales.manage') ? (
              <ActionButton
                label="Thêm khách hàng"
                onPress={() => openForm({
                  title: 'Thêm khách hàng',
                  submitLabel: 'Lưu khách hàng',
                  fields: [
                    { key: 'customer_code', label: 'Mã khách hàng', required: true },
                    { key: 'name', label: 'Họ tên', required: true },
                    { key: 'phone', label: 'Số điện thoại', keyboardType: 'numeric' },
                    { key: 'email', label: 'Email', keyboardType: 'email-address' },
                    { key: 'address', label: 'Địa chỉ' },
                    { key: 'note', label: 'Ghi chú' },
                  ],
                  onSubmit: (values) => queueRpc('Thêm khách hàng', 'save_customer', [values]),
                })}
              />
            ) : null}
            <ListView title="Khách hàng" rows={asRows(data.customers)} loading={loadingData} empty="Chưa có khách hàng." />
          </>
        ) : null}
        {tab === 'sales' ? (
          <SalesView
            customers={asRows(data.customers)}
            animals={asRows(data.saleableAnimals)}
            orders={asRows(data.orders)}
            reservations={asRows(data.reservations)}
            selectedCustomer={selectedCustomer}
            selectedAnimal={selectedAnimal}
            onSelectCustomer={setSelectedCustomer}
            onSelectAnimal={setSelectedAnimal}
            onQueueReservation={queueReservation}
            onCreateProductSale={openProductSaleForm}
            onRequestPayment={openPaymentForm}
            canRequest={api.can('sales.request') || api.can('sales.manage')}
            outboxReady={draftsLoaded}
          />
        ) : null}
        {tab === 'inventory' ? (
          <>
            {api.can('inventory.manage') ? (
              <>
                <ActionButton
                  label="Thêm mã hàng"
                  onPress={() => openForm({
                    title: 'Thêm mặt hàng vào catalog',
                    submitLabel: 'Lưu mặt hàng',
                    fields: [
                      { key: 'item_code', label: 'Mã SKU', required: true },
                      { key: 'name', label: 'Tên mặt hàng', required: true },
                      { key: 'category', label: 'Loại hàng', required: true, options: ['FOOD', 'MEDICINE', 'SUPPLIES'] },
                      { key: 'unit', label: 'Đơn vị', required: true, placeholder: 'gói, chai, kg...' },
                      { key: 'minimum_stock', label: 'Ngưỡng tồn thấp', keyboardType: 'decimal-pad' },
                      { key: 'retail_price', label: 'Giá bán (VND)', keyboardType: 'decimal-pad' },
                      { key: 'description', label: 'Mô tả' },
                    ],
                    onSubmit: (values) => queueRpc('Thêm mặt hàng kho', 'save_inventory_item', [{
                      ...values,
                      minimum_stock: Number(values.minimum_stock || 0),
                      retail_price: Number(values.retail_price || 0),
                      is_demo: false,
                    }]),
                  })}
                />
                <ActionButton
                  label="Nhập lô hàng"
                  onPress={() => openForm({
                    title: 'Nhập hàng vào kho',
                    description: 'Chọn mã mặt hàng từ danh sách và nhập đúng số lượng thực nhận.',
                    submitLabel: 'Gửi phiếu nhập',
                    fields: [
                      { key: 'item', label: 'Mặt hàng', required: true, options: mobileRecordOptions(asRows(data.items), 'item_code') },
                      { key: 'batch_code', label: 'Mã lô', required: true },
                      { key: 'quantity', label: 'Số lượng', keyboardType: 'decimal-pad', required: true },
                      { key: 'unit_cost', label: 'Giá nhập mỗi đơn vị (VND)', keyboardType: 'decimal-pad', required: true },
                      { key: 'expiry_date', label: 'Hạn sử dụng (YYYY-MM-DD)' },
                      { key: 'reference', label: 'Mã chứng từ' },
                    ],
                    onSubmit: (values) => queueRpc('Nhập lô hàng vào kho', 'receive_inventory_stock', [
                      optionId(values.item),
                      {
                        batch_code: values.batch_code,
                        quantity: Number(values.quantity),
                        unit_cost: Number(values.unit_cost),
                        expiry_date: values.expiry_date || null,
                        reference: values.reference || '',
                        occurred_on: localDateString(new Date()),
                        note: 'Nhập từ PetCare Mobile',
                      },
                    ]),
                  })}
                />
              </>
            ) : null}
            <ListView title="Tồn kho" rows={asRows(data.items)} loading={loadingData} empty="Chưa có mặt hàng trong kho." />
            <ListView title="Cảnh báo tồn thấp" rows={asRows(data.alerts)} empty="Không có cảnh báo tồn thấp." />
          </>
        ) : null}
        {tab === 'imports' ? (
          <>
            {api.can('imports.manage') ? (
              <ActionButton
                label="Thêm nhà cung cấp"
                onPress={() => openForm({
                  title: 'Thêm nhà cung cấp',
                  submitLabel: 'Lưu nhà cung cấp',
                  fields: [
                    { key: 'supplier_code', label: 'Mã nhà cung cấp', required: true },
                    { key: 'name', label: 'Tên nhà cung cấp', required: true },
                    { key: 'contact_person', label: 'Người liên hệ' },
                    { key: 'phone', label: 'Số điện thoại', keyboardType: 'numeric' },
                    { key: 'email', label: 'Email', keyboardType: 'email-address' },
                    { key: 'address', label: 'Địa chỉ' },
                    { key: 'tax_code', label: 'Mã số thuế' },
                  ],
                  onSubmit: (values) => queueRpc('Thêm nhà cung cấp', 'save_supplier', [values]),
                })}
              />
            ) : null}
            <ListView title="Nhà cung cấp" rows={asRows(data.suppliers)} loading={loadingData} empty="Chưa có nhà cung cấp." />
            <ListView title="Phiếu nhập" rows={asRows(data.batches)} empty="Chưa có phiếu nhập." />
          </>
        ) : null}
        {tab === 'store' ? (
          <>
            {api.can('store.manage') ? (
              <>
                <ActionButton
                  label="Thêm chuồng trại"
                  onPress={() => openForm({
                    title: 'Thêm chuồng trại',
                    submitLabel: 'Lưu chuồng',
                    fields: [
                      { key: 'cage_code', label: 'Mã chuồng', required: true },
                      { key: 'name', label: 'Tên chuồng', required: true },
                      { key: 'area', label: 'Khu vực' },
                      { key: 'accepted_species', label: 'Loài tiếp nhận' },
                      { key: 'capacity', label: 'Sức chứa', keyboardType: 'numeric', required: true },
                      { key: 'description', label: 'Ghi chú' },
                    ],
                    onSubmit: (values) => queueRpc('Thêm chuồng trại', 'save_cage', [{
                      ...values,
                      capacity: Number(values.capacity),
                    }]),
                  })}
                />
                {asRows(data.animals).length > 0 && asRows(data.cages).length > 0 ? (
                  <ActionButton
                    label="Xếp thú cưng vào chuồng"
                    onPress={() => openForm({
                      title: 'Xếp thú cưng vào chuồng',
                      submitLabel: 'Xác nhận xếp chuồng',
                      fields: [
                        { key: 'animal', label: 'Thú cưng', required: true, options: mobileRecordOptions(asRows(data.animals), 'animal_code') },
                        { key: 'cage', label: 'Chuồng', required: true, options: mobileRecordOptions(asRows(data.cages), 'cage_code') },
                        { key: 'note', label: 'Ghi chú' },
                      ],
                      onSubmit: (values) => queueRpc('Xếp thú cưng vào chuồng', 'assign_animal_to_cage', [
                        optionId(values.animal),
                        optionId(values.cage),
                        values.note || '',
                      ]),
                    })}
                  />
                ) : null}
              </>
            ) : null}
            <ListView title="Chuồng trại" rows={asRows(data.cages)} loading={loadingData} empty="Chưa có dữ liệu chuồng trại." />
          </>
        ) : null}
        {tab === 'care' ? (
          <>
            {api.can('care.manage') ? (
              <ActionButton
                label="Tạo công việc chăm sóc"
                onPress={() => openForm({
                  title: 'Tạo công việc chăm sóc',
                  submitLabel: 'Gửi công việc',
                  fields: [
                    { key: 'animal', label: 'Thú cưng', required: true, options: mobileRecordOptions(asRows(data.animals), 'animal_code') },
                    { key: 'title', label: 'Nội dung công việc', required: true },
                    { key: 'scheduled_at', label: 'Ngày thực hiện (YYYY-MM-DD)', initialValue: localDateString(new Date()), required: true },
                    { key: 'assigned_to', label: 'Người phụ trách' },
                    { key: 'note', label: 'Ghi chú' },
                  ],
                  onSubmit: (values) => queueRpc('Tạo công việc chăm sóc', 'add_care_task', [{
                    animal_id: optionId(values.animal),
                    title: values.title,
                    scheduled_at: values.scheduled_at,
                    assigned_to: values.assigned_to || api.user.display_name,
                    note: values.note || '',
                  }]),
                })}
              />
            ) : null}
            <ListView
              title="Công việc chăm sóc"
              rows={asRows(data.tasks)}
              loading={loadingData}
              empty="Chưa có công việc chăm sóc."
              rowAction={api.can('care.manage') ? (row) => ({
                label: row.is_completed ? 'Mở lại' : 'Hoàn tất',
                onPress: () => queueRpc(
                  `${row.is_completed ? 'Mở lại' : 'Hoàn tất'} ${displayName(row)}`,
                  'set_care_task_completed',
                  [Number(row.id), !row.is_completed],
                ),
              }) : undefined}
            />
          </>
        ) : null}
        {tab === 'health' ? (
          <>
            {api.can('health.manage') && asRows(data.animals).length > 0 ? (
              <ActionButton
                label="Thêm hồ sơ sức khỏe"
                onPress={() => openForm({
                  title: 'Ghi nhận sức khỏe',
                  submitLabel: 'Lưu hồ sơ',
                  fields: [
                    { key: 'animal', label: 'Thú cưng', required: true, options: mobileRecordOptions(asRows(data.animals), 'animal_code') },
                    { key: 'examination_date', label: 'Ngày khám (YYYY-MM-DD)', initialValue: localDateString(new Date()), required: true },
                    { key: 'health_status', label: 'Tình trạng', initialValue: 'Bình thường', options: ['Bình thường', 'Theo dõi', 'Đang điều trị', 'Cần khám'] },
                    { key: 'diagnosis', label: 'Chẩn đoán', required: true },
                    { key: 'treatment', label: 'Điều trị / hướng dẫn' },
                    { key: 'veterinarian', label: 'Bác sĩ thú y' },
                    { key: 'note', label: 'Ghi chú' },
                  ],
                  onSubmit: (values) => queueRpc('Thêm hồ sơ sức khỏe', 'add_health_record', [{
                    animal_id: optionId(values.animal),
                    examination_date: values.examination_date,
                    health_status: values.health_status || 'Bình thường',
                    diagnosis: values.diagnosis,
                    treatment: values.treatment || '',
                    veterinarian: values.veterinarian || '',
                    note: values.note || '',
                  }]),
                })}
              />
            ) : null}
            <ListView title="Hồ sơ sức khỏe" rows={asRows(data.health)} loading={loadingData} empty="Chưa có hồ sơ sức khỏe." />
            <ListView title="Lịch tiêm chủng" rows={asRows(data.vaccination)} empty="Chưa có lịch tiêm chủng." />
          </>
        ) : null}
        {tab === 'services' ? (
          <>
            {api.can('services.manage') && asRows(data.customers).length > 0 && asRows(data.packages).length > 0 ? (
              <ActionButton
                label="Đặt lịch dịch vụ"
                onPress={() => openForm({
                  title: 'Đặt lịch dịch vụ',
                  submitLabel: 'Gửi lịch hẹn',
                  fields: [
                    { key: 'customer', label: 'Khách hàng', required: true, options: mobileRecordOptions(asRows(data.customers), 'customer_code') },
                    { key: 'package', label: 'Gói dịch vụ', required: true, options: mobileRecordOptions(asRows(data.packages), 'code') },
                    { key: 'pet_name', label: 'Tên thú cưng', required: true },
                    { key: 'species', label: 'Loài', required: true, options: ['Chó', 'Mèo'] },
                    { key: 'coat_type', label: 'Loại lông', initialValue: 'SHORT', options: ['SHORT', 'LONG', 'DOUBLE', 'CURLY', 'THICK'] },
                    { key: 'scheduled_at', label: 'Ngày giờ (YYYY-MM-DDTHH:MM)', initialValue: `${localDateString(new Date())}T09:00`, required: true },
                    { key: 'weight_kg', label: 'Cân nặng (kg)', keyboardType: 'decimal-pad' },
                    { key: 'assigned_staff', label: 'Nhân viên phụ trách' },
                    { key: 'note', label: 'Ghi chú' },
                  ],
                  onSubmit: (values) => queueRpc('Đặt lịch dịch vụ', 'create_service_appointment', [{
                    customer_id: optionId(values.customer),
                    package_id: optionId(values.package),
                    pet_name: values.pet_name,
                    species: values.species,
                    coat_type: values.coat_type || 'SHORT',
                    scheduled_at: values.scheduled_at,
                    weight_kg: values.weight_kg ? Number(values.weight_kg) : null,
                    assigned_staff: values.assigned_staff || api.user.display_name,
                    note: values.note || '',
                  }]),
                })}
              />
            ) : null}
            <ListView
              title="Lịch hẹn dịch vụ"
              rows={asRows(data.appointments)}
              loading={loadingData}
              empty="Chưa có lịch hẹn dịch vụ."
              rowAction={api.can('services.manage') ? (row) => {
                const nextStatus: Record<string, { label: string; status: string }> = {
                  SCHEDULED: { label: 'Tiếp nhận', status: 'CHECKED_IN' },
                  CHECKED_IN: { label: 'Bắt đầu', status: 'IN_PROGRESS' },
                  IN_PROGRESS: { label: 'Hoàn tất', status: 'COMPLETED' },
                };
                const transition = nextStatus[String(row.status)];
                return transition ? {
                  label: transition.label,
                  onPress: () => queueRpc(
                    `${transition.label} lịch hẹn ${displayName(row)}`,
                    'update_service_appointment_status',
                    [Number(row.id), transition.status],
                  ),
                } : null;
              } : undefined}
            />
            <ListView title="Gói dịch vụ" rows={asRows(data.packages)} empty="Chưa có gói dịch vụ." />
          </>
        ) : null}
        {tab === 'memberships' ? (
          <>
            {api.can('membership.manage') && asRows(data.customers).length > 0 && asRows(data.plans).length > 0 ? (
              <ActionButton
                label="Tạo hội viên"
                onPress={() => openForm({
                  title: 'Đăng ký hội viên',
                  submitLabel: 'Tạo hội viên',
                  fields: [
                    { key: 'customer', label: 'Khách hàng', required: true, options: mobileRecordOptions(asRows(data.customers), 'customer_code') },
                    { key: 'plan', label: 'Gói thành viên', required: true, options: mobileRecordOptions(asRows(data.plans), 'code') },
                  ],
                  onSubmit: (values) => queueRpc('Đăng ký hội viên', 'create_membership', [
                    optionId(values.customer),
                    optionId(values.plan),
                  ]),
                })}
              />
            ) : null}
            <ListView title="Hội viên" rows={asRows(data.memberships)} loading={loadingData} empty="Chưa có hội viên." />
            <ListView title="Gói thành viên" rows={asRows(data.plans)} empty="Chưa có gói thành viên." />
            <ListView
              title="Hóa đơn hội viên"
              rows={asRows(data.bills)}
              empty="Chưa có hóa đơn hội viên."
              rowAction={api.can('membership.manage') ? (row) => (
                row.status === 'PAID' || row.status === 'CANCELLED' ? null : {
                  label: 'Ghi thanh toán',
                  onPress: () => openForm({
                    title: `Thanh toán hóa đơn ${displayName(row)}`,
                    submitLabel: 'Ghi nhận thanh toán',
                    fields: [
                      { key: 'amount', label: 'Số tiền (VND)', keyboardType: 'decimal-pad', required: true },
                      { key: 'method', label: 'Phương thức', required: true, options: ['CASH', 'BANK_TRANSFER', 'CARD', 'OTHER'] },
                      { key: 'reference', label: 'Mã giao dịch' },
                      { key: 'note', label: 'Ghi chú' },
                    ],
                    onSubmit: (values) => queueRpc('Ghi thanh toán hội viên', 'add_membership_bill_payment', [
                      Number(row.id),
                      {
                        amount: Number(values.amount),
                        method: values.method,
                        reference: values.reference || '',
                        note: values.note || '',
                        paid_at: localDateString(new Date()),
                      },
                    ]),
                  }),
                }
              ) : undefined}
            />
          </>
        ) : null}
        {tab === 'reports' ? (
          <>
            <ScreenHeader eyebrow="Tháng hiện tại" title="Báo cáo" subtitle="Tổng hợp bán hàng, tồn kho và sức khỏe." />
            <ListView title="Bán hàng" rows={asRows(data.sales)} loading={loadingData} empty="Chưa có dữ liệu bán hàng." />
            <ListView title="Tồn kho" rows={asRows(data.inventory)} empty="Chưa có dữ liệu tồn kho." />
            <ListView title="Sức khỏe" rows={asRows(data.health)} empty="Chưa có dữ liệu sức khỏe." />
          </>
        ) : null}
        {tab === 'team' ? (
          <>
            <ScreenHeader eyebrow="Quản trị" title="Nhân sự" subtitle={`Tổng tài khoản: ${text(data.userCount) || '—'}`} />
            {api.can('users.manage') ? (
              <ActionButton
                label="Tạo tài khoản nhân viên"
                onPress={() => openForm({
                  title: 'Tạo tài khoản',
                  description: 'Mật khẩu tạm thời phải được đổi khi nhân viên đăng nhập lần đầu.',
                  submitLabel: 'Tạo tài khoản',
                  fields: [
                    { key: 'username', label: 'Tên đăng nhập', required: true },
                    { key: 'display_name', label: 'Tên hiển thị', required: true },
                    { key: 'password', label: 'Mật khẩu tạm thời (ít nhất 12 ký tự)', required: true, secureTextEntry: true },
                    { key: 'role', label: 'Vai trò', required: true, options: ['MANAGER', 'VETERINARIAN', 'CAREGIVER', 'SALES', 'INVENTORY_MANAGER', 'SERVICE_COORDINATOR', 'CUSTOMER_SUPPORT', 'REPORT_ANALYST', 'AUDITOR'] },
                  ],
                  onSubmit: (values) => queueRpc('Tạo tài khoản nhân viên', 'create_user', [
                    values.username,
                    values.display_name,
                    values.password,
                    values.role,
                  ]),
                })}
              />
            ) : null}
            <ListView
              title="Tài khoản nhân viên"
              rows={asRows(data.users)}
              loading={loadingData}
              empty="Chưa có tài khoản."
              rowAction={api.can('users.manage') ? (row) => (
                Number(row.id) === api.user.id ? null : {
                  label: row.is_active ? 'Khóa' : 'Mở khóa',
                  onPress: () => Alert.alert(
                    row.is_active ? 'Khóa tài khoản' : 'Mở khóa tài khoản',
                    `Bạn có chắc muốn ${row.is_active ? 'khóa' : 'mở khóa'} ${displayName(row)}?`,
                    [
                      { text: 'Hủy', style: 'cancel' },
                      {
                        text: row.is_active ? 'Khóa' : 'Mở khóa',
                        style: row.is_active ? 'destructive' : 'default',
                        onPress: () => queueRpc(
                          `${row.is_active ? 'Khóa' : 'Mở khóa'} ${displayName(row)}`,
                          'set_user_active',
                          [Number(row.id), !row.is_active],
                        ),
                      },
                    ],
                  ),
                }
              ) : undefined}
            />
          </>
        ) : null}
        {tab === 'notifications' ? (
          <ListView title="Thông báo vận hành" rows={asRows(data.alerts)} loading={loadingData} empty="Không có cảnh báo mới." />
        ) : null}
        {tab === 'audit' ? (
          <ListView title="Nhật ký hoạt động" rows={asRows(data.events)} loading={loadingData} empty="Chưa có sự kiện ghi nhận." />
        ) : null}
        {tab === 'approvals' ? (
          <ApprovalView
            rows={asRows(data.approvals)}
            drafts={drafts}
            loading={loadingData}
            onReview={queueReview}
          />
        ) : null}
        <OutboxView drafts={drafts} onDismiss={dismissDraft} onRetry={retryDraft} />
      </ScrollView>
      <View style={styles.bottomAction}>
        <ActionButton
          busy={loadingData}
          label={loadingData ? 'Đang tải...' : 'Làm mới dữ liệu'}
          onPress={() => void loadTab()}
          secondary
        />
      </View>
      <ActionForm
        key={activeForm?.title ?? 'closed'}
        busy={false}
        description={activeForm?.description}
        fields={activeForm?.fields ?? []}
        onClose={() => setActiveForm(null)}
        onSubmit={(values) => activeForm?.onSubmit(values)}
        submitLabel={activeForm?.submitLabel ?? 'Lưu'}
        title={activeForm?.title ?? ''}
        visible={activeForm !== null}
      />
    </SafeAreaView>
  );
}

function AuthScreen({
  apiUrl,
  username,
  password,
  busy,
  error,
  onApiUrl,
  onUsername,
  onPassword,
  onSignIn,
  onCustomerStore,
}: {
  apiUrl: string;
  username: string;
  password: string;
  busy: boolean;
  error: string;
  onApiUrl: (value: string) => void;
  onUsername: (value: string) => void;
  onPassword: (value: string) => void;
  onSignIn: () => void;
  onCustomerStore: () => void;
}) {
  return (
    <AuthLayout>
      <ScreenHeader
        eyebrow="PetCare Central"
        title="Chào mừng trở lại"
        subtitle="Đăng nhập vào hệ thống quản lý PetCare của bạn."
      />
      <Field
        autoCapitalize="none"
        label="Địa chỉ API HTTPS"
        onChangeText={onApiUrl}
        placeholder="https://petcare.example.com"
        value={apiUrl}
      />
      <Field
        autoCapitalize="none"
        label="Tên đăng nhập"
        onChangeText={onUsername}
        placeholder="Tên tài khoản"
        value={username}
      />
      <Field
        label="Mật khẩu"
        onChangeText={onPassword}
        placeholder="Nhập mật khẩu"
        secureTextEntry
        value={password}
      />
      {error ? <ErrorBanner message={error} /> : null}
      <ActionButton busy={busy} label="Đăng nhập an toàn" onPress={onSignIn} />
      <ActionButton label="Mua hàng / tra cứu đơn" onPress={onCustomerStore} secondary />
      <Text style={styles.secureNote}>Kết nối được mã hóa bằng HTTPS. Mật khẩu không được lưu trên thiết bị.</Text>
    </AuthLayout>
  );
}

function PasswordScreen({
  busy,
  error,
  currentPassword,
  newPassword,
  confirmPassword,
  onCurrentPassword,
  onNewPassword,
  onConfirmPassword,
  onChange,
  onSignOut,
}: {
  busy: boolean;
  error: string;
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
  onCurrentPassword: (value: string) => void;
  onNewPassword: (value: string) => void;
  onConfirmPassword: (value: string) => void;
  onChange: () => void;
  onSignOut: () => void;
}) {
  return (
    <AuthLayout>
      <ScreenHeader
        eyebrow="Bảo mật tài khoản"
        title="Đổi mật khẩu"
        subtitle="Bạn cần thay mật khẩu tạm thời trước khi tiếp tục."
      />
      <Field label="Mật khẩu hiện tại" onChangeText={onCurrentPassword} secureTextEntry value={currentPassword} />
      <Field label="Mật khẩu mới (ít nhất 12 ký tự)" onChangeText={onNewPassword} secureTextEntry value={newPassword} />
      <Field label="Xác nhận mật khẩu mới" onChangeText={onConfirmPassword} secureTextEntry value={confirmPassword} />
      {error ? <ErrorBanner message={error} /> : null}
      <ActionButton busy={busy} label="Cập nhật mật khẩu" onPress={onChange} />
      <ActionButton label="Đăng xuất" onPress={onSignOut} secondary />
    </AuthLayout>
  );
}

function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.authRoot}>
        <ScrollView contentContainerStyle={styles.authContent} keyboardShouldPersistTaps="handled">
          <View style={styles.authBrand}>
            <View style={styles.brandMark}><Text style={styles.brandMarkText}>P</Text></View>
            <Text style={styles.brandName}>PetCare</Text>
          </View>
          <Surface style={styles.authCard}>{children}</Surface>
          <Text style={styles.secureNote}>Quản lý chăm sóc thú cưng, bán hàng và vận hành — mọi lúc mọi nơi.</Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function DashboardView({
  data,
  loading,
  onRefresh,
}: {
  data: DataSet;
  loading: boolean;
  onRefresh: () => void;
}) {
  const counts = asRecord(data.counts);
  const recent = asRows(data.recent);
  const countItems = [
    ['Tổng thú cưng', counts.TOTAL],
    ['Đang bán', counts.AVAILABLE],
    ['Đang giữ chỗ', counts.RESERVED],
    ['Chờ kiểm tra', counts.PENDING_INSPECTION],
  ] as const;
  return (
    <>
      <ScreenHeader eyebrow="Không gian làm việc" title="Tổng quan" subtitle="Tình hình vận hành mới nhất của cửa hàng." />
      <View style={styles.metricGrid}>
        {countItems.map(([label, value]) => (
          <Surface key={label} style={styles.metricCard}>
            <Text style={styles.metricValue}>{loading && value === undefined ? '—' : String(value ?? 0)}</Text>
            <Text style={styles.metricLabel}>{label}</Text>
          </Surface>
        ))}
      </View>
      <ListView title="Thú cưng mới cập nhật" rows={recent} empty="Chưa có thú cưng mới." />
      <ListView title="Cảnh báo vận hành" rows={asRows(data.alerts)} empty="Không có cảnh báo mới." />
      <ActionButton label="Cập nhật tổng quan" onPress={onRefresh} secondary />
    </>
  );
}

function SalesView({
  customers,
  animals,
  orders,
  reservations,
  selectedCustomer,
  selectedAnimal,
  onSelectCustomer,
  onSelectAnimal,
  onQueueReservation,
  onCreateProductSale,
  onRequestPayment,
  canRequest,
  outboxReady,
}: {
  customers: Record<string, unknown>[];
  animals: Record<string, unknown>[];
  orders: Record<string, unknown>[];
  reservations: Record<string, unknown>[];
  selectedCustomer: Record<string, unknown> | null;
  selectedAnimal: Record<string, unknown> | null;
  onSelectCustomer: (row: Record<string, unknown> | null) => void;
  onSelectAnimal: (row: Record<string, unknown> | null) => void;
  onQueueReservation: () => void;
  onCreateProductSale: () => void;
  onRequestPayment: (row: Record<string, unknown>) => void;
  canRequest: boolean;
  outboxReady: boolean;
}) {
  return (
    <>
      <ScreenHeader eyebrow="Hoạt động cửa hàng" title="Bán hàng" subtitle="Đơn hàng, lượt giữ chỗ và yêu cầu bán hàng." />
      {canRequest ? (
        <ActionButton
          disabled={!outboxReady}
          label={outboxReady ? 'Tạo đơn bán sản phẩm / combo' : 'Đang tải hàng đợi...'}
          onPress={onCreateProductSale}
        />
      ) : null}
      <ListView
        title="Đơn hàng gần đây"
        rows={orders}
        empty="Chưa có đơn hàng."
        rowAction={canRequest ? (row) => (
          row.status === 'PAID' || row.status === 'CANCELLED' ? null : {
            label: 'Ghi thanh toán',
            onPress: () => onRequestPayment(row),
          }
        ) : undefined}
      />
      <ListView title="Lượt giữ chỗ" rows={reservations} empty="Chưa có lượt giữ chỗ." />
      {canRequest ? (
        <Surface>
          <Text style={styles.sectionTitle}>Tạo yêu cầu giữ chỗ</Text>
          <Text style={styles.sectionHint}>Thao tác được gửi lên máy chủ khi có mạng; nếu ngoại tuyến sẽ được lưu để đồng bộ.</Text>
          <Text style={styles.fieldLabel}>Chọn khách hàng</Text>
          {selectedCustomer ? (
            <SelectedRow row={selectedCustomer} onClear={() => onSelectCustomer(null)} />
          ) : (
            customers.slice(0, 8).map((row, index) => (
              <ChoiceRow
                key={String(row.id ?? index)}
                title={displayName(row)}
                detail={text(row.phone)}
                onPress={() => onSelectCustomer(row)}
              />
            ))
          )}
          <Text style={styles.fieldLabel}>Chọn thú cưng còn bán</Text>
          {selectedAnimal ? (
            <SelectedRow row={selectedAnimal} onClear={() => onSelectAnimal(null)} />
          ) : (
            animals.filter((row) => row.status === 'AVAILABLE').slice(0, 8).map((row, index) => (
              <ChoiceRow
                key={String(row.id ?? index)}
                title={displayName(row)}
                detail={`${text(row.species)} · ${formatMoney(row.sale_price)}`}
                onPress={() => onSelectAnimal(row)}
              />
            ))
          )}
          <ActionButton
            disabled={!outboxReady}
            label={outboxReady ? 'Gửi yêu cầu giữ chỗ' : 'Đang tải hàng đợi...'}
            onPress={onQueueReservation}
          />
        </Surface>
      ) : null}
    </>
  );
}

function ListView({
  title,
  rows,
  loading,
  empty,
  rowAction,
}: {
  title: string;
  rows: Record<string, unknown>[];
  loading?: boolean;
  empty: string;
  rowAction?: (row: Record<string, unknown>) => { label: string; onPress: () => void } | null;
}) {
  const [query, setQuery] = useState('');
  const [visibleCount, setVisibleCount] = useState(12);
  const filtered = rows.filter((row) => {
    if (!query.trim()) return true;
    return JSON.stringify(row).toLocaleLowerCase('vi').includes(query.trim().toLocaleLowerCase('vi'));
  });
  return (
    <Surface>
      <Text style={styles.sectionTitle}>{title}</Text>
      {rows.length > 12 ? (
        <Field label="Tìm trong danh sách" onChangeText={setQuery} placeholder={`Tìm ${title.toLocaleLowerCase('vi')}...`} value={query} />
      ) : null}
      {loading && rows.length === 0 ? (
        <ActivityIndicator color={colors.forest} style={styles.inlineLoading} />
      ) : filtered.length === 0 ? (
        <Text style={styles.emptyInline}>{empty}</Text>
      ) : filtered.slice(0, visibleCount).map((row, index) => {
        const action = rowAction?.(row);
        return (
          <View key={String(row.id ?? row.order_code ?? row.request_code ?? index)} style={styles.listRow}>
            <View style={styles.listRowCopy}>
              <Text numberOfLines={1} style={styles.listRowTitle}>{displayName(row)}</Text>
              <Text numberOfLines={2} style={styles.listRowDetail}>{rowDetail(row)}</Text>
            </View>
            {action ? (
              <Pressable accessibilityRole="button" onPress={action.onPress} style={styles.rowAction}>
                <Text style={styles.rowActionText}>{action.label}</Text>
              </Pressable>
            ) : (
              <View style={styles.rowBadge}>
                <Text style={styles.rowBadgeText}>{text(row.status ?? row.health_status ?? row.species ?? '—')}</Text>
              </View>
            )}
          </View>
        );
      })}
      {filtered.length > visibleCount ? (
        <Pressable onPress={() => setVisibleCount((count) => count + 12)} style={styles.loadMore}>
          <Text style={styles.loadMoreText}>Tải thêm · {filtered.length - visibleCount} mục</Text>
        </Pressable>
      ) : null}
      {query && filtered.length !== rows.length ? <Text style={styles.sectionHint}>Tìm thấy {filtered.length} trong {rows.length} mục.</Text> : null}
    </Surface>
  );
}

function OutboxView({
  drafts,
  onRetry,
  onDismiss,
}: {
  drafts: RpcDraft[];
  onRetry: (draft: RpcDraft) => void;
  onDismiss: (draft: RpcDraft) => void;
}) {
  if (drafts.length === 0) return null;
  return (
    <Surface>
      <Text style={styles.sectionTitle}>Hàng đợi đồng bộ ({drafts.length})</Text>
      {drafts.map((draft) => (
        <View key={draft.requestId} style={styles.draftRow}>
          <View style={styles.listRowCopy}>
            <Text style={styles.listRowTitle}>{draft.title}</Text>
            <Text style={styles.listRowDetail}>
              {draft.status === 'queued' ? 'Đang chờ đồng bộ' : 'Cần kiểm tra trạng thái'}
              {draft.error ? ` · ${draft.error}` : ''}
            </Text>
          </View>
          {draft.status === 'needs-review' ? (
            <View style={styles.draftActions}>
              <Pressable onPress={() => onRetry(draft)} style={styles.retryButton}>
                <Text style={styles.retryText}>Kiểm tra</Text>
              </Pressable>
              <Pressable onPress={() => onDismiss(draft)} style={styles.dismissButton}>
                <Text style={styles.dismissButtonText}>Xóa</Text>
              </Pressable>
            </View>
          ) : null}
        </View>
      ))}
    </Surface>
  );
}

function ApprovalView({
  rows,
  drafts,
  loading,
  onReview,
}: {
  rows: Record<string, unknown>[];
  drafts: RpcDraft[];
  loading: boolean;
  onReview: (row: Record<string, unknown>, approve: boolean) => void;
}) {
  if (loading && rows.length === 0) {
    return <Surface><ActivityIndicator color={colors.forest} /></Surface>;
  }
  if (rows.length === 0) {
    return <EmptyState title="Không có yêu cầu cần duyệt" detail="Các yêu cầu mới sẽ xuất hiện tại đây." />;
  }
  return (
    <>
      <ScreenHeader eyebrow="Quy trình bán hàng" title="Duyệt yêu cầu" subtitle="Xem nội dung và quyết định các yêu cầu đang chờ." />
      {rows.map((row, index) => {
        const pending = row.status === 'PENDING';
        const queued = drafts.some(
          (draft) =>
            draft.method === 'review_sales_approval_request' &&
            Number(draft.args[0]) === Number(row.id),
        );
        return (
          <Surface key={String(row.id ?? index)}>
            <View style={styles.approvalHeader}>
              <Text style={styles.listRowTitle}>{text(row.request_code) || `Yêu cầu #${text(row.id)}`}</Text>
              <View style={styles.rowBadge}><Text style={styles.rowBadgeText}>{text(row.status)}</Text></View>
            </View>
            <Text style={styles.listRowDetail}>
              {text(row.action_type)} · {text(row.requester_name ?? row.requester_username)} · {text(row.created_at)}
            </Text>
            {pending ? (
              <View style={styles.approvalActions}>
                <ActionButton
                  disabled={queued}
                  label={queued ? 'Đang chờ xác nhận' : 'Duyệt'}
                  onPress={() => onReview(row, true)}
                />
                <ActionButton
                  disabled={queued}
                  label="Từ chối"
                  onPress={() => onReview(row, false)}
                  secondary
                />
              </View>
            ) : null}
          </Surface>
        );
      })}
    </>
  );
}

function ChoiceRow({
  title,
  detail,
  onPress,
}: {
  title: string;
  detail: string;
  onPress: () => void;
}) {
  return (
    <Pressable accessibilityRole="button" onPress={onPress} style={({ pressed }) => [styles.choiceRow, pressed && styles.choicePressed]}>
      <View style={styles.choiceCopy}>
        <Text numberOfLines={1} style={styles.listRowTitle}>{title}</Text>
        {detail ? <Text numberOfLines={1} style={styles.listRowDetail}>{detail}</Text> : null}
      </View>
      <Text style={styles.choicePlus}>+</Text>
    </Pressable>
  );
}

function SelectedRow({
  row,
  onClear,
}: {
  row: Record<string, unknown>;
  onClear: () => void;
}) {
  return (
    <View style={styles.selectedRow}>
      <Text numberOfLines={1} style={styles.listRowTitle}>{displayName(row)}</Text>
      <Pressable accessibilityRole="button" onPress={onClear}>
        <Text style={styles.clearSelection}>Đổi</Text>
      </Pressable>
    </View>
  );
}

function ErrorBanner({ message, onDismiss }: { message: string; onDismiss?: () => void }) {
  return (
    <View accessibilityRole="alert" style={styles.errorBanner}>
      <Text style={styles.errorText}>{message}</Text>
      {onDismiss ? <Pressable onPress={onDismiss}><Text style={styles.dismissText}>Đóng</Text></Pressable> : null}
    </View>
  );
}

function LoadingScreen({ label }: { label: string }) {
  return (
    <SafeAreaView style={styles.loadingScreen}>
      <ActivityIndicator color={colors.forest} size="large" />
      <Text style={styles.loadingText}>{label}</Text>
      <StatusBar style="dark" />
    </SafeAreaView>
  );
}

function asRows(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object')
    : [];
}

function asRecord(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {};
}

function text(value: unknown): string {
  return value === null || value === undefined || value === '' ? '' : String(value);
}

function displayName(row: Record<string, unknown>): string {
  return text(row.name ?? row.animal_name ?? row.customer_name ?? row.order_code ?? row.request_code ?? row.item_code ?? row.title ?? row.id) || 'Chưa có tên';
}

function rowDetail(row: Record<string, unknown>): string {
  const parts = [
    row.animal_code ?? row.customer_code ?? row.species ?? row.order_code ?? row.request_code,
    row.customer_name ?? row.animal_name ?? row.item_code,
    row.created_at ?? row.reserved_at ?? row.order_date ?? row.date,
    row.total_amount !== undefined ? formatMoney(row.total_amount) : undefined,
  ].map(text).filter(Boolean);
  return parts.join(' · ') || 'Không có thông tin bổ sung';
}

function formatMoney(value: unknown): string {
  const amount = Number(value);
  return Number.isFinite(amount) && amount > 0
    ? `${new Intl.NumberFormat('vi-VN').format(amount)} ₫`
    : '—';
}

function describeResult(value: unknown): string {
  const result = asRecord(value);
  if (result.request_code) return `Mã yêu cầu: ${text(result.request_code)}`;
  if (result.status === 'PENDING') return 'Đã gửi để chờ phê duyệt.';
  return result.status === 'APPLIED' ? 'Thao tác đã được hệ thống tiếp nhận.' : 'Máy chủ đã xác nhận hoàn tất.';
}

function errorMessage(reason: unknown): string {
  return reason instanceof Error ? reason.message : 'Đã xảy ra lỗi không xác định.';
}

function localDateString(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function mobileRecordOptions(
  rows: Record<string, unknown>[],
  codeField: string,
): string[] {
  return rows
    .filter((row) => Number.isInteger(Number(row.id)) && Number(row.id) > 0)
    .map((row) => `${text(row.id)} · ${text(row[codeField]) || displayName(row)} · ${displayName(row)}`);
}

function optionId(value: string): number {
  const parsed = Number(value.split(' · ', 1)[0]);
  if (!Number.isInteger(parsed) || parsed < 1) {
    throw new Error('Vui lòng chọn một mục hợp lệ trong danh sách.');
  }
  return parsed;
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: colors.paper, flex: 1 },
  authRoot: { flex: 1 },
  authContent: { flexGrow: 1, justifyContent: 'center', padding: spacing.lg },
  authBrand: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm, justifyContent: 'center', marginBottom: spacing.lg },
  authCard: { padding: spacing.lg },
  secureNote: { color: colors.muted, fontSize: 12, lineHeight: 18, marginTop: spacing.md, textAlign: 'center' },
  appHeader: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  brandMark: { alignItems: 'center', backgroundColor: colors.forest, borderRadius: 14, height: 42, justifyContent: 'center', width: 42 },
  brandMarkText: { color: colors.white, fontSize: 22, fontWeight: '900' },
  brandCopy: { flex: 1 },
  brandName: { color: colors.ink, fontSize: 19, fontWeight: '900', letterSpacing: 0.2 },
  brandUser: { color: colors.muted, fontSize: 11, marginTop: 2 },
  signOutButton: { backgroundColor: colors.white, borderColor: colors.line, borderRadius: 11, borderWidth: 1, paddingHorizontal: 12, paddingVertical: 9 },
  signOutText: { color: colors.forest, fontSize: 12, fontWeight: '800' },
  connectionBar: { alignItems: 'center', flexDirection: 'row', gap: 7, minHeight: 30, paddingHorizontal: spacing.md },
  connectionDot: { borderRadius: 5, height: 8, width: 8 },
  onlineDot: { backgroundColor: '#3E9B67' },
  offlineDot: { backgroundColor: colors.amber },
  connectionText: { color: colors.muted, flex: 1, fontSize: 11 },
  outboxCount: { color: colors.amber, fontSize: 10, fontWeight: '800' },
  tabs: { gap: 8, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  tab: { backgroundColor: colors.white, borderColor: colors.line, borderRadius: 20, borderWidth: 1, paddingHorizontal: 15, paddingVertical: 9 },
  activeTab: { backgroundColor: colors.forest, borderColor: colors.forest },
  tabText: { color: colors.muted, fontSize: 12, fontWeight: '700' },
  activeTabText: { color: colors.white },
  content: { flexGrow: 1, padding: spacing.md, paddingBottom: spacing.xl },
  bottomAction: { backgroundColor: colors.paper, borderTopColor: colors.line, borderTopWidth: 1, padding: spacing.md },
  metricGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginBottom: spacing.sm },
  metricCard: { flexBasis: '47%', flexGrow: 1, marginBottom: 0, minHeight: 92, padding: spacing.md },
  metricValue: { color: colors.forest, fontSize: 25, fontWeight: '900' },
  metricLabel: { color: colors.muted, fontSize: 11, fontWeight: '600', marginTop: 5 },
  sectionTitle: { color: colors.ink, fontSize: 16, fontWeight: '800', marginBottom: spacing.sm },
  sectionHint: { color: colors.muted, fontSize: 12, lineHeight: 18, marginBottom: spacing.sm },
  fieldLabel: { color: colors.ink, fontSize: 13, fontWeight: '700', marginBottom: spacing.xs },
  listRow: { alignItems: 'center', borderTopColor: colors.line, borderTopWidth: 1, flexDirection: 'row', gap: spacing.sm, paddingVertical: 12 },
  listRowCopy: { flex: 1, gap: 4 },
  listRowTitle: { color: colors.ink, fontSize: 13, fontWeight: '700' },
  listRowDetail: { color: colors.muted, fontSize: 11, lineHeight: 16 },
  rowBadge: { backgroundColor: colors.mint, borderRadius: 10, maxWidth: 98, paddingHorizontal: 8, paddingVertical: 5 },
  rowBadgeText: { color: colors.forest, fontSize: 9, fontWeight: '800' },
  rowAction: { backgroundColor: colors.mint, borderRadius: 10, paddingHorizontal: 9, paddingVertical: 7 },
  rowActionText: { color: colors.forest, fontSize: 10, fontWeight: '800' },
  loadMore: { alignItems: 'center', borderTopColor: colors.line, borderTopWidth: 1, paddingTop: spacing.sm },
  loadMoreText: { color: colors.forest, fontSize: 12, fontWeight: '800' },
  emptyInline: { color: colors.muted, fontSize: 13, paddingVertical: 10 },
  inlineLoading: { paddingVertical: spacing.md },
  errorBanner: { alignItems: 'center', backgroundColor: colors.redWash, borderColor: '#F5CDCD', borderRadius: 12, borderWidth: 1, flexDirection: 'row', gap: spacing.sm, justifyContent: 'space-between', marginBottom: spacing.md, padding: spacing.md },
  errorText: { color: colors.red, flex: 1, fontSize: 12, lineHeight: 18 },
  dismissText: { color: colors.red, fontSize: 11, fontWeight: '800' },
  cacheNotice: { color: colors.amber, fontSize: 11, marginBottom: spacing.sm },
  choiceRow: { alignItems: 'center', borderColor: colors.line, borderRadius: 12, borderWidth: 1, flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.xs, padding: 11 },
  choiceCopy: { flex: 1, gap: 3 },
  choicePressed: { backgroundColor: colors.mint },
  choicePlus: { color: colors.forest, fontSize: 19, fontWeight: '700' },
  selectedRow: { alignItems: 'center', backgroundColor: colors.mint, borderRadius: 12, flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.sm, padding: 12 },
  clearSelection: { color: colors.forest, fontSize: 12, fontWeight: '800', padding: 5 },
  draftRow: { alignItems: 'center', borderTopColor: colors.line, borderTopWidth: 1, flexDirection: 'row', gap: spacing.sm, paddingVertical: spacing.sm },
  approvalHeader: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.xs },
  approvalActions: { gap: spacing.xs, marginTop: spacing.md },
  draftActions: { alignItems: 'flex-end', gap: 5 },
  retryButton: { backgroundColor: colors.amberWash, borderRadius: 10, paddingHorizontal: 10, paddingVertical: 8 },
  retryText: { color: colors.amber, fontSize: 10, fontWeight: '800' },
  dismissButton: { paddingHorizontal: 10, paddingVertical: 5 },
  dismissButtonText: { color: colors.red, fontSize: 10, fontWeight: '700' },
  loadingScreen: { alignItems: 'center', backgroundColor: colors.paper, flex: 1, gap: spacing.md, justifyContent: 'center' },
  loadingText: { color: colors.muted, fontSize: 13 },
});

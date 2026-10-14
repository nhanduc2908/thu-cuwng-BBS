import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { createRequestId, validateApiUrl } from './api';
import { ActionButton, EmptyState, Field, ScreenHeader, Surface } from './components';
import { saveApiUrl } from './storage';
import { colors, spacing } from './theme';
import type { StorefrontCatalog, StorefrontItem } from './types';

type StorefrontTab = 'catalog' | 'cart' | 'tracking';

export function CustomerStorefront({
  apiUrl,
  onApiUrl,
  onBack,
}: {
  apiUrl: string;
  onApiUrl: (value: string) => void;
  onBack: () => void;
}) {
  const [catalog, setCatalog] = useState<StorefrontCatalog | null>(null);
  const [cart, setCart] = useState<Record<string, number>>({});
  const [search, setSearch] = useState('');
  const [tab, setTab] = useState<StorefrontTab>('catalog');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [note, setNote] = useState('');
  const [consent, setConsent] = useState(false);
  const [requestCode, setRequestCode] = useState('');
  const [trackingCode, setTrackingCode] = useState('');
  const [trackingResult, setTrackingResult] = useState<Record<string, unknown> | null>(null);
  const [trackingBusy, setTrackingBusy] = useState(false);
  const pendingCheckout = useRef<{ fingerprint: string; requestId: string } | null>(null);

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const baseUrl = validateApiUrl(apiUrl);
      const response = await fetch(`${baseUrl}/api/storefront/catalog`, {
        headers: { Accept: 'application/json' },
      });
      const payload = await readJson(response);
      if (!Array.isArray(payload.products) || !Array.isArray(payload.combos)) {
        throw new Error('Central API trả về catalog không hợp lệ.');
      }
      setCatalog(payload as StorefrontCatalog);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    if (!apiUrl.trim()) return;
    const timer = setTimeout(() => void loadCatalog(), 450);
    return () => clearTimeout(timer);
  }, [apiUrl, loadCatalog]);

  const items = useMemo(() => {
    const query = search.trim().toLocaleLowerCase('vi');
    return [...(catalog?.products ?? []), ...(catalog?.combos ?? [])]
      .filter((item) => !item.is_demo && Number(item.retail_price) > 0)
      .filter((item) => Number(item.usable_quantity) >= 5)
      .filter((item) => !query || `${item.name} ${item.item_code} ${item.description ?? ''}`.toLocaleLowerCase('vi').includes(query));
  }, [catalog, search]);

  const cartItems = useMemo(
    () =>
      [...(catalog?.products ?? []), ...(catalog?.combos ?? [])]
        .filter((item) => cart[item.item_code] > 0)
        .map((item) => ({ item, quantity: cart[item.item_code] })),
    [catalog, cart],
  );
  const cartCount = Object.values(cart).reduce((total, quantity) => total + quantity, 0);
  const cartTotal = cartItems.reduce(
    (total, line) => total + effectivePrice(line.item) * line.quantity,
    0,
  );

  const changeQuantity = (item: StorefrontItem, delta: number) => {
    setCart((current) => {
      const maxAvailable = Math.min(99, Math.floor(Number(item.usable_quantity)));
      const nextQuantity = Math.max(0, Math.min(maxAvailable, (current[item.item_code] ?? 0) + delta));
      const next = { ...current };
      if (nextQuantity === 0) delete next[item.item_code];
      else next[item.item_code] = nextQuantity;
      return next;
    });
  };

  const submitOrder = async () => {
    if (!customerName.trim() || !phone.trim()) {
      setError('Vui lòng nhập họ tên và số điện thoại.');
      return;
    }
    if (!consent) {
      setError('Bạn cần đồng ý gửi thông tin đặt hàng đến cửa hàng.');
      return;
    }
    if (cartItems.length === 0) {
      setError('Giỏ hàng đang trống.');
      return;
    }
    const fingerprint = JSON.stringify({
      name: customerName.trim(),
      phone: phone.trim(),
      address: address.trim(),
      note: note.trim(),
      items: cartItems.map(({ item, quantity }) => [item.item_code, quantity]),
    });
    if (pendingCheckout.current?.fingerprint !== fingerprint) {
      pendingCheckout.current = { fingerprint, requestId: createRequestId() };
    }
    setSubmitting(true);
    setError('');
    try {
      const baseUrl = validateApiUrl(apiUrl);
      await saveApiUrl(baseUrl);
      const response = await fetch(`${baseUrl}/api/storefront/order-requests`, {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: customerName.trim(),
          phone: phone.trim(),
          address: address.trim(),
          note: note.trim(),
          consent: true,
          clientRequestId: pendingCheckout.current.requestId,
          items: cartItems.map(({ item, quantity }) => ({
            id: item.item_code,
            quantity,
          })),
        }),
      });
      const result = await readJson(response);
      if (typeof result.requestCode !== 'string') {
        throw new Error('Central API chưa trả mã tham chiếu đơn hàng.');
      }
      setRequestCode(result.requestCode);
      setTrackingCode(result.requestCode);
      setCart({});
      setConsent(false);
      pendingCheckout.current = null;
      setTab('tracking');
      await loadCatalog();
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setSubmitting(false);
    }
  };

  const lookupOrder = async () => {
    const code = trackingCode.trim().toUpperCase();
    if (!code) {
      setError('Nhập mã tham chiếu đơn hàng để tra cứu.');
      return;
    }
    setTrackingBusy(true);
    setError('');
    setTrackingResult(null);
    try {
      const baseUrl = validateApiUrl(apiUrl);
      const response = await fetch(
        `${baseUrl}/api/storefront/order-requests/${encodeURIComponent(code)}`,
        { headers: { Accept: 'application/json' } },
      );
      const result = await readJson(response);
      if (result.requestCode !== code) {
        throw new Error('Mã tham chiếu không khớp với đơn hàng.');
      }
      setTrackingResult(result);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setTrackingBusy(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <View style={styles.headerCopy}>
          <Text style={styles.brand}>Bông Bông Pet Care</Text>
          <Text style={styles.subBrand}>Cửa hàng trực tuyến</Text>
        </View>
        <Pressable accessibilityRole="button" onPress={onBack} style={styles.backButton}>
          <Text style={styles.backText}>Nhân viên</Text>
        </Pressable>
      </View>
      <View style={styles.tabs}>
        {([
          ['catalog', 'Sản phẩm'],
          ['cart', `Giỏ hàng${cartCount ? ` · ${cartCount}` : ''}`],
          ['tracking', 'Tra cứu đơn'],
        ] as const).map(([key, label]) => (
          <Pressable
            accessibilityRole="tab"
            accessibilityState={{ selected: tab === key }}
            key={key}
            onPress={() => {
              setError('');
              setTab(key);
            }}
            style={[styles.tab, tab === key && styles.activeTab]}
          >
            <Text style={[styles.tabText, tab === key && styles.activeTabText]}>{label}</Text>
          </Pressable>
        ))}
      </View>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        {error ? <Surface><Text accessibilityRole="alert" style={styles.error}>{error}</Text></Surface> : null}
        {!apiUrl.trim() ? (
          <Surface>
            <ScreenHeader title="Kết nối cửa hàng" subtitle="Nhập địa chỉ Central API HTTPS mà nhân viên dùng chung." />
            <Field
              autoCapitalize="none"
              label="Địa chỉ Central API HTTPS"
              onChangeText={onApiUrl}
              placeholder="https://petcare.example.com"
              value={apiUrl}
            />
            <ActionButton label="Tải catalog" onPress={() => void loadCatalog()} />
          </Surface>
        ) : null}
        {tab === 'catalog' ? (
          <>
            <ScreenHeader
              eyebrow="Mua sắm"
              title="Sản phẩm cho thú cưng"
              subtitle="Danh mục và tồn kho được lấy trực tiếp từ hệ thống PetCare."
              action={<Pressable onPress={() => void loadCatalog()}><Text style={styles.refresh}>Làm mới</Text></Pressable>}
            />
            <Field label="Tìm sản phẩm" onChangeText={setSearch} placeholder="Tên, mã sản phẩm..." value={search} />
            {loading && !catalog ? <ActivityIndicator color={colors.forest} /> : null}
            {items.length === 0 && !loading ? (
              <EmptyState title="Chưa có sản phẩm phù hợp" detail="Sản phẩm demo, hết hàng hoặc chưa có giá sẽ không hiển thị để đặt mua." />
            ) : items.slice(0, 60).map((item) => (
              <ProductCard
                item={item}
                key={item.item_code}
                quantity={cart[item.item_code] ?? 0}
                disabled={(cart[item.item_code] ?? 0) >= Math.floor(Number(item.usable_quantity))}
                onAdd={() => changeQuantity(item, 1)}
              />
            ))}
            {items.length > 60 ? <Text style={styles.hint}>Đang hiển thị 60 trong {items.length} sản phẩm phù hợp. Hãy tìm kiếm để thu hẹp danh sách.</Text> : null}
          </>
        ) : null}
        {tab === 'cart' ? (
          <>
            <ScreenHeader eyebrow="Đơn hàng" title="Giỏ hàng" subtitle="Đơn tạo từ cửa hàng sẽ chờ nhân viên xác nhận thanh toán." />
            {cartItems.length === 0 ? <EmptyState title="Giỏ hàng đang trống" detail="Chọn sản phẩm từ danh mục để bắt đầu." /> : (
              <>
                <Surface>
                  {cartItems.map(({ item, quantity }) => (
                    <View key={item.item_code} style={styles.cartRow}>
                      <View style={styles.productCopy}>
                        <Text style={styles.productName}>{item.name}</Text>
                        <Text style={styles.hint}>{formatMoney(effectivePrice(item))} · {item.item_code}</Text>
                      </View>
                      <QuantityControl item={item} quantity={quantity} onChange={changeQuantity} />
                    </View>
                  ))}
                  <View style={styles.totalRow}>
                    <Text style={styles.totalLabel}>Tạm tính</Text>
                    <Text style={styles.total}>{formatMoney(cartTotal)}</Text>
                  </View>
                </Surface>
                <Surface>
                  <Text style={styles.sectionTitle}>Thông tin nhận hàng</Text>
                  <Field label="Họ tên *" onChangeText={setCustomerName} value={customerName} />
                  <Field keyboardType="numeric" label="Số điện thoại *" onChangeText={setPhone} value={phone} />
                  <Field label="Địa chỉ" onChangeText={setAddress} value={address} />
                  <Field label="Ghi chú" onChangeText={setNote} value={note} />
                  <Pressable
                    accessibilityRole="checkbox"
                    accessibilityState={{ checked: consent }}
                    onPress={() => setConsent((value) => !value)}
                    style={styles.consent}
                  >
                    <View style={[styles.checkbox, consent && styles.checked]}>{consent ? <Text style={styles.checkmark}>✓</Text> : null}</View>
                    <Text style={styles.consentText}>Tôi đồng ý gửi thông tin liên hệ và đơn hàng đến cửa hàng.</Text>
                  </Pressable>
                  <ActionButton busy={submitting} label="Gửi yêu cầu đặt hàng" onPress={() => void submitOrder()} />
                </Surface>
              </>
            )}
          </>
        ) : null}
        {tab === 'tracking' ? (
          <>
            <ScreenHeader eyebrow="Theo dõi" title="Kiểm tra đơn hàng" subtitle="Chỉ cần mã tham chiếu; tra cứu không hiển thị thông tin cá nhân." />
            {requestCode ? <Surface><Text style={styles.sectionTitle}>Mã đơn vừa tạo</Text><Text selectable style={styles.requestCode}>{requestCode}</Text></Surface> : null}
            <Surface>
              <Field autoCapitalize="characters" label="Mã tham chiếu" onChangeText={setTrackingCode} placeholder="BBR-..." value={trackingCode} />
              <ActionButton busy={trackingBusy} label="Tra cứu trạng thái" onPress={() => void lookupOrder()} />
            </Surface>
            {trackingResult ? (
              <Surface>
                <Text style={styles.sectionTitle}>Trạng thái đơn</Text>
                <InfoRow label="Yêu cầu" value={String(trackingResult.status ?? '—')} />
                <InfoRow label="Mã đơn bán" value={String(trackingResult.salesOrderCode ?? '—')} />
                <InfoRow label="Thanh toán" value={String(trackingResult.salesOrderStatus ?? '—')} />
                <InfoRow label="Tổng tiền" value={formatMoney(trackingResult.salesOrderTotal)} />
                <InfoRow label="Đã xuất kho" value={trackingResult.inventoryFulfilled ? 'Có' : 'Chưa'} />
              </Surface>
            ) : null}
          </>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

function ProductCard({
  item,
  quantity,
  disabled,
  onAdd,
}: {
  item: StorefrontItem;
  quantity: number;
  disabled: boolean;
  onAdd: () => void;
}) {
  return (
    <Surface>
      <Text style={styles.productName}>{item.name}</Text>
      <Text style={styles.hint}>{item.catalog_category || item.category || (item.type === 'combo' ? 'Combo' : 'Sản phẩm')} · {item.item_code}</Text>
      {item.description ? <Text style={styles.description}>{item.description}</Text> : null}
      <View style={styles.productFooter}>
        <View style={styles.productCopy}>
          <Text style={styles.price}>{formatMoney(effectivePrice(item))}</Text>
          <Text style={styles.hint}>Còn khả dụng: {Math.floor(Number(item.usable_quantity))}</Text>
        </View>
        <ActionButton disabled={disabled} label={disabled ? 'Đã đạt tồn khả dụng' : quantity > 0 ? `Thêm nữa (${quantity})` : 'Thêm vào giỏ'} onPress={onAdd} />
      </View>
    </Surface>
  );
}

function QuantityControl({
  item,
  quantity,
  onChange,
}: {
  item: StorefrontItem;
  quantity: number;
  onChange: (item: StorefrontItem, delta: number) => void;
}) {
  return (
    <View style={styles.quantityControl}>
      <Pressable accessibilityLabel="Giảm số lượng" onPress={() => onChange(item, -1)} style={styles.quantityButton}><Text style={styles.quantityButtonText}>−</Text></Pressable>
      <Text style={styles.quantity}>{quantity}</Text>
      <Pressable accessibilityLabel="Tăng số lượng" onPress={() => onChange(item, 1)} style={styles.quantityButton}><Text style={styles.quantityButtonText}>+</Text></Pressable>
    </View>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

function effectivePrice(item: StorefrontItem): number {
  const price = Number(item.retail_price);
  const promotion = Math.min(100, Math.max(0, Number(item.promotion_percent) || 0));
  return Math.round(price * (1 - promotion / 100));
}

function formatMoney(value: unknown): string {
  const amount = Number(value);
  return Number.isFinite(amount)
    ? `${new Intl.NumberFormat('vi-VN').format(amount)} ₫`
    : '—';
}

async function readJson(response: Response): Promise<Record<string, any>> {
  let payload: Record<string, any>;
  try {
    payload = await response.json();
  } catch {
    throw new Error(`Central API trả về phản hồi không hợp lệ (HTTP ${response.status}).`);
  }
  if (!response.ok) {
    throw new Error(typeof payload.detail === 'string' ? payload.detail : `Yêu cầu thất bại (HTTP ${response.status}).`);
  }
  return payload;
}

function errorMessage(reason: unknown): string {
  return reason instanceof Error ? reason.message : 'Không thể kết nối Central API.';
}

const styles = StyleSheet.create({
  safeArea: { backgroundColor: colors.paper, flex: 1 },
  header: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  headerCopy: { flex: 1 },
  brand: { color: colors.ink, fontSize: 18, fontWeight: '900' },
  subBrand: { color: colors.muted, fontSize: 11, marginTop: 2 },
  backButton: { backgroundColor: colors.white, borderColor: colors.line, borderRadius: 12, borderWidth: 1, paddingHorizontal: 12, paddingVertical: 10 },
  backText: { color: colors.forest, fontSize: 12, fontWeight: '800' },
  tabs: { flexDirection: 'row', gap: spacing.xs, paddingHorizontal: spacing.md, paddingVertical: spacing.sm },
  tab: { alignItems: 'center', backgroundColor: colors.white, borderColor: colors.line, borderRadius: 20, borderWidth: 1, flex: 1, paddingHorizontal: 6, paddingVertical: 10 },
  activeTab: { backgroundColor: colors.forest, borderColor: colors.forest },
  tabText: { color: colors.muted, fontSize: 11, fontWeight: '700' },
  activeTabText: { color: colors.white },
  content: { padding: spacing.md, paddingBottom: spacing.xl },
  refresh: { color: colors.forest, fontSize: 12, fontWeight: '800', paddingTop: 5 },
  error: { color: colors.red, fontSize: 13, lineHeight: 19 },
  sectionTitle: { color: colors.ink, fontSize: 16, fontWeight: '800', marginBottom: spacing.sm },
  productName: { color: colors.ink, fontSize: 15, fontWeight: '800' },
  productCopy: { flex: 1, gap: 4 },
  hint: { color: colors.muted, fontSize: 11, lineHeight: 16 },
  description: { color: colors.muted, fontSize: 12, lineHeight: 18, marginTop: spacing.sm },
  productFooter: { alignItems: 'center', borderTopColor: colors.line, borderTopWidth: 1, flexDirection: 'row', gap: spacing.sm, marginTop: spacing.md, paddingTop: spacing.sm },
  price: { color: colors.forest, fontSize: 16, fontWeight: '900' },
  cartRow: { alignItems: 'center', borderBottomColor: colors.line, borderBottomWidth: 1, flexDirection: 'row', gap: spacing.sm, paddingVertical: spacing.sm },
  quantityControl: { alignItems: 'center', flexDirection: 'row', gap: 8 },
  quantityButton: { alignItems: 'center', backgroundColor: colors.mint, borderRadius: 10, height: 34, justifyContent: 'center', width: 34 },
  quantityButtonText: { color: colors.forest, fontSize: 19, fontWeight: '800' },
  quantity: { color: colors.ink, fontSize: 14, fontWeight: '800', minWidth: 20, textAlign: 'center' },
  totalRow: { alignItems: 'center', flexDirection: 'row', justifyContent: 'space-between', paddingTop: spacing.md },
  totalLabel: { color: colors.ink, fontSize: 14, fontWeight: '700' },
  total: { color: colors.forest, fontSize: 18, fontWeight: '900' },
  consent: { alignItems: 'center', flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.md },
  checkbox: { alignItems: 'center', borderColor: colors.line, borderRadius: 6, borderWidth: 1, height: 22, justifyContent: 'center', width: 22 },
  checked: { backgroundColor: colors.forest, borderColor: colors.forest },
  checkmark: { color: colors.white, fontSize: 14, fontWeight: '900' },
  consentText: { color: colors.muted, flex: 1, fontSize: 12, lineHeight: 18 },
  requestCode: { color: colors.forest, fontSize: 18, fontWeight: '900', letterSpacing: 1 },
  infoRow: { borderTopColor: colors.line, borderTopWidth: 1, flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10 },
  infoLabel: { color: colors.muted, fontSize: 12 },
  infoValue: { color: colors.ink, fontSize: 12, fontWeight: '700', maxWidth: '60%', textAlign: 'right' },
});

# PetCare Mobile

Ứng dụng React Native/Expo dùng chung Central API của PetCare, chạy trên Android
và iOS. Dự án mobile, cấu hình và hướng dẫn build đều nằm trong thư mục này.

## Yêu cầu

- Node.js phiên bản LTS hiện hành.
- Central API PetCare đang chạy và được công khai qua HTTPS với chứng chỉ TLS hợp lệ.
- Expo Go để chạy thử trên thiết bị hoặc Android Studio/Xcode cho trình giả lập.

## Cài đặt và chạy

Từ thư mục `mobile`:

```powershell
npm ci
npm run typecheck
npm start
```

Quét mã QR bằng Expo Go hoặc chọn trình giả lập Android/iOS trong giao diện Expo.
Ứng dụng yêu cầu nhập URL HTTPS của Central API ở màn hình đăng nhập; không nhập
URL HTTP hoặc địa chỉ localhost khi chạy trên thiết bị thật.

## Khu vực khách hàng và nhân viên

- Màn hình đầu cho phép chọn đăng nhập nhân viên hoặc **Mua hàng / tra cứu đơn**.
- Cửa hàng mobile tải catalog trực tiếp từ Central API, tìm kiếm SKU/combo,
  tạo giỏ hàng và gửi đơn sau khi khách đồng ý cung cấp thông tin. Chỉ mặt hàng
  không phải demo, có giá và còn ít nhất 5 đơn vị mới được đặt. Đơn được tạo
  chung với cửa hàng HTML và desktop, ở trạng thái chờ thanh toán; ứng dụng
  không tự thu tiền.
- Khách hàng có thể tra cứu trạng thái bằng mã tham chiếu. Kết quả không chứa
  tên, số điện thoại hay địa chỉ. Lỗi máy chủ/kết nối được hiển thị rõ ràng;
  cửa hàng không dùng dữ liệu catalog cũ để giả làm dữ liệu trực tiếp.
- Khu vực nhân viên ẩn các tab theo quyền Central API. Ngoài xem dashboard,
  hồ sơ và báo cáo, các thao tác di động hiện hỗ trợ tạo hồ sơ thú cưng/khách
  hàng/nhà cung cấp, nhập hàng, tạo SKU, phân chuồng, tạo việc chăm sóc/ghi
  nhận sức khỏe/đặt lịch dịch vụ/đăng ký hội viên, ghi thanh toán hội viên,
  tạo đơn bán tối đa một SKU và một combo, ghi nhận thanh toán đơn hàng, quản lý tài
  khoản và duyệt yêu cầu. Đơn bán và thanh toán đi qua quy trình yêu cầu/duyệt
  hiện có; thao tác được gửi qua RPC có xác thực và ghi hàng đợi để có thể đồng
  bộ an toàn. Giá bán, tồn kho và quyền nghiệp vụ vẫn được máy chủ kiểm tra.
- Danh sách lớn có tìm kiếm và tải thêm kết quả thay vì chỉ hiển thị 12 dòng.

## Build Android và iOS

Cài EAS CLI (`npm install --global eas-cli`), đăng nhập Expo (`eas login`), sau
đó chạy các lệnh từ thư mục này:

```powershell
eas build --platform android --profile preview
eas build --platform ios --profile preview
```

Profile `preview` tạo APK cài thử Android và bản iOS Simulator. Để phát hành
Android, chạy `eas build --platform android --profile production`. Bản iOS phân
phối lên thiết bị thật cần tài khoản Apple Developer và signing credentials:

```powershell
eas build --platform ios --profile production
```

EAS thực hiện build native trên máy chủ; không cần macOS/Xcode cục bộ trên
Windows. Trước khi phát hành, thay `com.petcare.central` trong `app.json` bằng
bundle/package ID riêng đã đăng ký cho ứng dụng.

## Phiên và dữ liệu ngoại tuyến

- Access/refresh token được lưu trong SecureStore của hệ điều hành; mật khẩu
  không được lưu.
- API URL, cache đọc và hàng đợi thao tác được lưu trong AsyncStorage và phân
  vùng theo ID tài khoản.
- Cache chỉ được dùng khi thiết bị không kết nối được tới máy chủ; máy chủ từ
  chối yêu cầu sẽ hiển thị lỗi, không thay bằng dữ liệu cũ.
- Yêu cầu bán hàng ngoại tuyến được gắn request ID duy nhất. Khi đồng bộ, app
  tra cứu request ID trước và chỉ gửi thao tác với cùng ID nếu máy chủ chưa ghi
  nhận yêu cầu đó. Trạng thái đang xử lý/thất bại cần được kiểm tra lại trong
  hàng đợi.
- Phân quyền giao diện chỉ hỗ trợ trải nghiệm; Central API vẫn là nơi xác thực
  quyền cuối cùng.

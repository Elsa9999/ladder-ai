# Mẫu AI_Tags.xml (SimaticML Tag Table)

Sử dụng mẫu này để tạo bảng tag định dạng SimaticML. Tất cả tên biến (Tag name) bắt buộc viết bằng tiếng Việt không dấu (ASCII), nhưng phần chú thích (Comment) bắt buộc phải dùng tiếng Việt có dấu chuẩn UTF-8.

## Mẫu XML chuẩn

```xml
<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="V18" />
  <DocumentInfo>
    <Created>2026-05-23T00:00:00Z</Created>
    <ExportSetting>WithDefaults</ExportSetting>
  </DocumentInfo>
  <SW.Tags.PlcTagTable ID="0">
    <AttributeList>
      <Name>AI_Tags</Name>
    </AttributeList>
    <ObjectList>
      <SW.Tags.PlcTag ID="1" CompositionName="Tags">
        <AttributeList>
          <DataTypeName>Bool</DataTypeName>
          <LogicalAddress>%I0.0</LogicalAddress>
          <Name>AI_Nut_Khoi_Dong</Name>
          <Comment>Nút khởi động vật lý</Comment>
        </AttributeList>
      </SW.Tags.PlcTag>
      <SW.Tags.PlcTag ID="2" CompositionName="Tags">
        <AttributeList>
          <DataTypeName>Bool</DataTypeName>
          <LogicalAddress>%M0.0</LogicalAddress>
          <Name>AI_Nut_Khoi_Dong_HMI</Name>
          <Comment>Lệnh khởi động từ HMI hoặc PLCSIM</Comment>
        </AttributeList>
      </SW.Tags.PlcTag>
    </ObjectList>
  </SW.Tags.PlcTagTable>
</Document>
```

## Ghi chú quan trọng

- Thuộc tính `ID` trong toàn bộ bảng tag phải là duy nhất.
- Địa chỉ vùng nhớ `%M` cần được phân hoạch khoa học, tránh trùng lặp với Clock Memory của PLC.
- Bảng tag phải được nhập (Import) vào TIA Portal trước khi nhập các khối chương trình (Block XML).

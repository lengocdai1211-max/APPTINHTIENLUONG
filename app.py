
import streamlit as st
import pandas as pd
from io import BytesIO

# ==================================================
# 1. CẤU HÌNH ỨNG DỤNG
# ==================================================
st.set_page_config(
    page_title="Quản lý và tính lương hàng loạt",
    page_icon="💰",
    layout="wide"
)

MAX_NHAN_VIEN = 500

COT_DU_LIEU = [
    "Mã nhân viên",
    "Họ và tên",
    "Lương cơ bản",
    "Tiền thưởng",
    "Phụ cấp có BHXH",
    "Phụ cấp không BHXH",
    "Số người phụ thuộc"
]

COT_SO = [
    "Lương cơ bản",
    "Tiền thưởng",
    "Phụ cấp có BHXH",
    "Phụ cấp không BHXH",
    "Số người phụ thuộc"
]

COT_KET_QUA = [
    "Tổng thu nhập",
    "Tiền đóng bảo hiểm",
    "Giảm trừ bản thân",
    "Giảm trừ người phụ thuộc",
    "Thu nhập tính thuế",
    "Thuế TNCN",
    "Thực lãnh"
]


# ==================================================
# 2. HÀM HỖ TRỢ
# ==================================================
def dinh_dang_tien(so_tien):
    return f"{so_tien:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tinh_thue_tncn(thu_nhap_tinh_thue):
    """
    Biểu thuế theo công thức trong code gốc.
    Đơn vị: triệu đồng/tháng.
    """
    thu_nhap_tinh_thue = max(0.0, thu_nhap_tinh_thue)

    if thu_nhap_tinh_thue <= 10:
        return thu_nhap_tinh_thue * 0.05
    elif thu_nhap_tinh_thue <= 30:
        return thu_nhap_tinh_thue * 0.10 - 0.5
    elif thu_nhap_tinh_thue <= 60:
        return thu_nhap_tinh_thue * 0.20 - 3.5
    elif thu_nhap_tinh_thue <= 100:
        return thu_nhap_tinh_thue * 0.30 - 9.5
    else:
        return thu_nhap_tinh_thue * 0.35 - 14.5


def tao_du_lieu_mau(so_luong):
    """Tạo bảng nhập liệu cho số lượng nhân viên được chọn."""
    return pd.DataFrame({
        "Mã nhân viên": [f"NV{i:03d}" for i in range(1, so_luong + 1)],
        "Họ và tên": [f"Nhân viên {i}" for i in range(1, so_luong + 1)],
        "Lương cơ bản": [10.0] * so_luong,
        "Tiền thưởng": [1.0] * so_luong,
        "Phụ cấp có BHXH": [1.0] * so_luong,
        "Phụ cấp không BHXH": [0.5] * so_luong,
        "Số người phụ thuộc": [0] * so_luong
    })


def chuan_hoa_du_lieu(df):
    """Đưa dữ liệu tải lên về đúng tên cột và kiểm tra kiểu dữ liệu."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Hỗ trợ một số cách viết tên cột thường gặp
    ten_cot_thay_the = {
        "Mã NV": "Mã nhân viên",
        "Tên nhân viên": "Họ và tên",
        "Họ tên": "Họ và tên",
        "Lương cơ bản (triệu đồng)": "Lương cơ bản",
        "Tiền thưởng (triệu đồng)": "Tiền thưởng",
        "Phụ cấp có tính BHXH": "Phụ cấp có BHXH",
        "Phụ cấp không tính BHXH": "Phụ cấp không BHXH",
        "Số người phụ thuộc (người)": "Số người phụ thuộc"
    }
    df = df.rename(columns=ten_cot_thay_the)

    # Bổ sung cột còn thiếu
    if "Mã nhân viên" not in df.columns:
        df["Mã nhân viên"] = [f"NV{i:03d}" for i in range(1, len(df) + 1)]

    if "Họ và tên" not in df.columns:
        df["Họ và tên"] = [f"Nhân viên {i}" for i in range(1, len(df) + 1)]

    for cot in COT_SO:
        if cot not in df.columns:
            df[cot] = 0

        df[cot] = pd.to_numeric(df[cot], errors="coerce").fillna(0)

    df["Mã nhân viên"] = df["Mã nhân viên"].fillna("").astype(str)
    df["Họ và tên"] = df["Họ và tên"].fillna("").astype(str)

    return df[COT_DU_LIEU].head(MAX_NHAN_VIEN).reset_index(drop=True)


def tinh_bang_luong(df):
    """Tính thu nhập, bảo hiểm, thuế và thực lãnh cho từng nhân viên."""
    ket_qua = df.copy()

    # Bảo đảm dữ liệu số hợp lệ
    for cot in COT_SO:
        ket_qua[cot] = pd.to_numeric(
            ket_qua[cot], errors="coerce"
        ).fillna(0)

    # Không cho phép khoản thu nhập hoặc số người phụ thuộc âm
    for cot in COT_SO:
        ket_qua[cot] = ket_qua[cot].clip(lower=0)

    ket_qua["Số người phụ thuộc"] = (
        ket_qua["Số người phụ thuộc"].round().astype(int)
    )

    # Tổng thu nhập
    ket_qua["Tổng thu nhập"] = (
        ket_qua["Lương cơ bản"]
        + ket_qua["Tiền thưởng"]
        + ket_qua["Phụ cấp có BHXH"]
        + ket_qua["Phụ cấp không BHXH"]
    )

    # Khoản bảo hiểm theo giả định trong code gốc
    ket_qua["Tiền đóng bảo hiểm"] = (
        ket_qua["Lương cơ bản"] + ket_qua["Phụ cấp có BHXH"]
    ) * 0.105

    # Các khoản giảm trừ theo code gốc
    ket_qua["Giảm trừ bản thân"] = 15.5
    ket_qua["Giảm trừ người phụ thuộc"] = (
        ket_qua["Số người phụ thuộc"] * 6.2
    )

    # Thu nhập tính thuế
    ket_qua["Thu nhập tính thuế"] = (
        ket_qua["Tổng thu nhập"]
        - ket_qua["Tiền đóng bảo hiểm"]
        - ket_qua["Giảm trừ bản thân"]
        - ket_qua["Giảm trừ người phụ thuộc"]
    ).clip(lower=0)

    # Thuế TNCN
    ket_qua["Thuế TNCN"] = ket_qua["Thu nhập tính thuế"].apply(
        tinh_thue_tncn
    )

    # Tiền thực lãnh
    ket_qua["Thực lãnh"] = (
        ket_qua["Tổng thu nhập"]
        - ket_qua["Tiền đóng bảo hiểm"]
        - ket_qua["Thuế TNCN"]
    )

    return ket_qua


def tao_file_excel(df_chi_tiet):
    """Xuất Excel gồm bảng lương chi tiết và bảng tổng hợp."""
    output = BytesIO()

    cot_xuat = COT_DU_LIEU + COT_KET_QUA
    bang_xuat = df_chi_tiet[cot_xuat].copy()

    dong_tong = {
        "Mã nhân viên": "",
        "Họ và tên": "TỔNG CỘNG"
    }

    for cot in COT_SO:
        dong_tong[cot] = ""

    for cot in COT_KET_QUA:
        dong_tong[cot] = bang_xuat[cot].sum()

    bang_tong = pd.DataFrame([dong_tong])

    tong_hop = pd.DataFrame({
        "Chỉ tiêu": [
            "Số lượng nhân viên",
            "Tổng thu nhập",
            "Tổng tiền đóng bảo hiểm",
            "Tổng thu nhập tính thuế",
            "Tổng thuế TNCN",
            "Tổng tiền thực lãnh",
            "Thực lãnh bình quân/người"
        ],
        "Giá trị (triệu đồng)": [
            len(df_chi_tiet),
            df_chi_tiet["Tổng thu nhập"].sum(),
            df_chi_tiet["Tiền đóng bảo hiểm"].sum(),
            df_chi_tiet["Thu nhập tính thuế"].sum(),
            df_chi_tiet["Thuế TNCN"].sum(),
            df_chi_tiet["Thực lãnh"].sum(),
            df_chi_tiet["Thực lãnh"].mean()
            if len(df_chi_tiet) > 0 else 0
        ]
    })

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        bang_xuat.to_excel(
            writer, sheet_name="Bang_luong_chi_tiet", index=False
        )
        bang_tong.to_excel(
            writer, sheet_name="Bang_luong_chi_tiet",
            index=False, startrow=len(bang_xuat) + 2, header=False
        )
        tong_hop.to_excel(
            writer, sheet_name="Tong_hop", index=False
        )

        # Định dạng độ rộng cột và tiêu đề
        for ten_sheet in writer.sheets:
            ws = writer.sheets[ten_sheet]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = (
                f"A1:{ws.cell(row=1, column=ws.max_column).coordinate}"
            )

            for cells in ws.columns:
                max_length = 0
                letter = cells[0].column_letter

                for cell in cells:
                    if cell.value is not None:
                        max_length = max(max_length, len(str(cell.value)))

                ws.column_dimensions[letter].width = min(max_length + 3, 32)

        ws = writer.sheets["Bang_luong_chi_tiet"]

        # Định dạng số cho các cột tiền
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '#,##0.000'

    output.seek(0)
    return output.getvalue()


# ==================================================
# 3. GIAO DIỆN
# ==================================================
st.title("💰 ỨNG DỤNG TÍNH LƯƠNG VÀ THUẾ TNCN")
st.markdown(
    "Tính lương hàng loạt cho tối đa **500 người lao động** "
    "và xuất báo cáo Excel."
)
st.caption(
    "Đơn vị tiền tệ: triệu đồng/tháng. "
    "Công thức thuế và bảo hiểm đang sử dụng theo code gốc."
)

st.divider()

# ==================================================
# 4. CHỌN PHƯƠNG THỨC NHẬP DỮ LIỆU
# ==================================================
st.header("1. Chọn cách nhập dữ liệu")

phuong_thuc = st.radio(
    "Bạn muốn nhập dữ liệu bằng cách nào?",
    [
        "Nhập trực tiếp trên ứng dụng",
        "Tải danh sách từ file Excel"
    ],
    horizontal=True
)

df_nguon = None

if phuong_thuc == "Tải danh sách từ file Excel":
    st.markdown(
        "File Excel cần có các cột: **Mã nhân viên, Họ và tên, "
        "Lương cơ bản, Tiền thưởng, Phụ cấp có BHXH, "
        "Phụ cấp không BHXH, Số người phụ thuộc**."
    )

    # Tạo file mẫu để tải xuống
    file_mau = BytesIO()
    with pd.ExcelWriter(file_mau, engine="openpyxl") as writer:
        tao_du_lieu_mau(3).to_excel(
            writer, sheet_name="Danh_sach_nhan_vien", index=False
        )
    file_mau.seek(0)

    st.download_button(
        "📥 Tải file Excel mẫu",
        data=file_mau.getvalue(),
        file_name="mau_danh_sach_nhan_vien.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    file_tai_len = st.file_uploader(
        "Chọn file Excel danh sách nhân viên",
        type=["xlsx"]
    )

    if file_tai_len is not None:
        try:
            df_doc = pd.read_excel(file_tai_len)
            df_nguon = chuan_hoa_du_lieu(df_doc)

            if len(df_doc) > MAX_NHAN_VIEN:
                st.warning(
                    "File có hơn 500 dòng. Ứng dụng chỉ lấy tối đa 500 nhân viên đầu tiên."
                )

            st.success(
                f"Đã đọc được {len(df_nguon)} dòng nhân viên từ file Excel."
            )
        except Exception as e:
            st.error(f"Không đọc được file Excel: {e}")

# ==================================================
# 5. CHỌN SỐ LƯỢNG NHÂN VIÊN
# ==================================================
st.header("2. Chọn số lượng người lao động cần tính")

if phuong_thuc == "Tải danh sách từ file Excel" and df_nguon is not None:
    gioi_han = max(1, min(MAX_NHAN_VIEN, len(df_nguon)))

    so_nhan_vien = st.number_input(
        "Số nhân viên cần tính (tối đa 500)",
        min_value=1,
        max_value=gioi_han,
        value=gioi_han,
        step=1
    )

    df_nhap = df_nguon.head(int(so_nhan_vien)).copy()

elif phuong_thuc == "Tải danh sách từ file Excel":
    st.info("Vui lòng tải file Excel lên trước khi tiếp tục.")
    st.stop()

else:
    so_nhan_vien = st.number_input(
        "Số nhân viên cần tính (tối đa 500)",
        min_value=1,
        max_value=MAX_NHAN_VIEN,
        value=10,
        step=1
    )

    df_nhap = tao_du_lieu_mau(int(so_nhan_vien))

st.caption(
    f"Số lượng nhân viên được chọn: **{int(so_nhan_vien)} người**."
)

# ==================================================
# 6. NHẬP HOẶC CHỈNH SỬA DỮ LIỆU
# ==================================================
st.header("3. Nhập và kiểm tra bảng lương đầu vào")

st.write(
    "Bạn có thể chỉnh sửa trực tiếp các ô trong bảng. "
    "Các khoản thu nhập nhập theo triệu đồng."
)

df_da_sua = st.data_editor(
    df_nhap,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    key="bang_nhap_luong",
    column_config={
        "Mã nhân viên": st.column_config.TextColumn(
            "Mã nhân viên", required=True
        ),
        "Họ và tên": st.column_config.TextColumn(
            "Họ và tên", required=True
        ),
        "Lương cơ bản": st.column_config.NumberColumn(
            "Lương cơ bản", min_value=0.0, step=0.5, format="%.3f"
        ),
        "Tiền thưởng": st.column_config.NumberColumn(
            "Tiền thưởng", min_value=0.0, step=0.5, format="%.3f"
        ),
        "Phụ cấp có BHXH": st.column_config.NumberColumn(
            "Phụ cấp có BHXH", min_value=0.0, step=0.5, format="%.3f"
        ),
        "Phụ cấp không BHXH": st.column_config.NumberColumn(
            "Phụ cấp không BHXH", min_value=0.0, step=0.5, format="%.3f"
        ),
        "Số người phụ thuộc": st.column_config.NumberColumn(
            "Số người phụ thuộc",
            min_value=0,
            max_value=100,
            step=1,
            format="%d"
        )
    }
)

# ==================================================
# 7. NÚT TÍNH LƯƠNG
# ==================================================
st.divider()

if st.button(
    "🧮 TÍNH LƯƠNG CHO TOÀN BỘ NHÂN VIÊN",
    type="primary",
    use_container_width=True
):
    if df_da_sua["Mã nhân viên"].astype(str).str.strip().eq("").any():
        st.error("Vui lòng nhập đầy đủ mã nhân viên.")
        st.stop()

    if df_da_sua["Họ và tên"].astype(str).str.strip().eq("").any():
        st.error("Vui lòng nhập đầy đủ họ và tên nhân viên.")
        st.stop()

    if df_da_sua["Mã nhân viên"].duplicated().any():
        st.error("Mã nhân viên bị trùng. Vui lòng kiểm tra lại.")
        st.stop()

    if df_da_sua[COT_SO].isna().any().any():
        st.error("Có ô số liệu bị bỏ trống hoặc không hợp lệ.")
        st.stop()

    if (df_da_sua[COT_SO] < 0).any().any():
        st.error("Không nhập số âm cho thu nhập hoặc số người phụ thuộc.")
        st.stop()

    if not (
        df_da_sua["Số người phụ thuộc"]
        .apply(lambda x: float(x).is_integer())
        .all()
    ):
        st.error("Số người phụ thuộc phải là số nguyên.")
        st.stop()

    df_ket_qua = tinh_bang_luong(df_da_sua)

    # Lưu kết quả vào session state để tải Excel không bị mất
    st.session_state["ket_qua_luong"] = df_ket_qua

# ==================================================
# 8. HIỂN THỊ KẾT QUẢ
# ==================================================
if "ket_qua_luong" in st.session_state:
    df_ket_qua = st.session_state["ket_qua_luong"]

    st.divider()
    st.header("4. Kết quả tính lương")

    tong_nhan_vien = len(df_ket_qua)
    tong_thu_nhap = df_ket_qua["Tổng thu nhập"].sum()
    tong_bao_hiem = df_ket_qua["Tiền đóng bảo hiểm"].sum()
    tong_thue = df_ket_qua["Thuế TNCN"].sum()
    tong_thuc_lanh = df_ket_qua["Thực lãnh"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Số nhân viên", f"{tong_nhan_vien:,} người")
    c2.metric("Tổng quỹ lương", f"{dinh_dang_tien(tong_thu_nhap)} triệu")
    c3.metric("Tổng thực lãnh", f"{dinh_dang_tien(tong_thuc_lanh)} triệu")

    c4, c5, c6 = st.columns(3)
    c4.metric("Tổng bảo hiểm", f"{dinh_dang_tien(tong_bao_hiem)} triệu")
    c5.metric("Tổng thuế TNCN", f"{dinh_dang_tien(tong_thue)} triệu")
    c6.metric(
        "Thực lãnh bình quân",
        f"{dinh_dang_tien(df_ket_qua['Thực lãnh'].mean())} triệu"
    )

    st.subheader("Bảng lương chi tiết từng nhân viên")

    cot_hien_thi = COT_DU_LIEU + COT_KET_QUA
    df_hien_thi = df_ket_qua[cot_hien_thi].copy()

    cot_tien = COT_SO + COT_KET_QUA
    for cot in cot_tien:
        if cot in df_hien_thi.columns:
            df_hien_thi[cot] = df_hien_thi[cot].round(3)

    st.dataframe(
        df_hien_thi,
        use_container_width=True,
        hide_index=True,
        height=500
    )

    st.subheader("Biểu đồ phân bổ tổng thu nhập")

    bieu_do = pd.DataFrame({
        "Khoản mục": [
            "Tiền thực lãnh",
            "Tiền đóng bảo hiểm",
            "Thuế TNCN"
        ],
        "Số tiền (triệu đồng)": [
            tong_thuc_lanh,
            tong_bao_hiem,
            tong_thue
        ]
    })

    st.bar_chart(
        bieu_do.set_index("Khoản mục"),
        y="Số tiền (triệu đồng)"
    )

    st.subheader("5. Xuất báo cáo Excel")

    file_excel = tao_file_excel(df_ket_qua)

    st.download_button(
        label="📥 TẢI BẢNG LƯƠNG EXCEL (.xlsx)",
        data=file_excel,
        file_name="bao_cao_tinh_luong.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.caption(
        "File Excel gồm bảng lương chi tiết từng nhân viên và bảng tổng hợp "
        "quỹ lương, bảo hiểm, thuế TNCN, tiền thực lãnh."
    )

    st.info(
        "Kết quả được tính theo công thức trong code gốc. "
        "Trước khi dùng để trả lương thực tế, cần cập nhật mức giảm trừ, "
        "biểu thuế và quy định bảo hiểm theo kỳ tính lương áp dụng."
    )
else:
    st.info(
        "Nhập hoặc tải danh sách nhân viên, chọn số lượng cần tính, "
        "kiểm tra dữ liệu rồi nhấn nút tính lương."
    )

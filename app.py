
import streamlit as st
import os
st.image("LOGOJPG.jpg")
import pandas as pd

# =========================
# CẤU HÌNH ỨNG DỤNG
# =========================
st.set_page_config(
    page_title="Tính lương thực lãnh",
    page_icon="💰",
    layout="wide"
)

# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def dinh_dang_tien(so_tien):
    return f"{so_tien:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".")


# =========================
# HÀM TÍNH THUẾ TNCN
# =========================
def tinh_thue_tncn(thu_nhap_tinh_thue):
    # Thu nhập tính thuế âm hoặc bằng 0 thì không phát sinh thuế
    thu_nhap_tinh_thue = max(0, thu_nhap_tinh_thue)

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


# =========================
# TIÊU ĐỀ
# =========================
st.title("💰 PHẦN MỀM TÍNH TIỀN LƯƠNG-LÊ NGỌC ĐẠI")
st.subheader("Tính thu nhập và tiền lương thực lãnh của người lao động")
st.caption(
    "Đơn vị tính: triệu đồng/tháng. "
    "Các mức tính toán được giữ theo code gốc do người dùng cung cấp."
)

st.divider()

# =========================
# NHẬP THÔNG TIN
# =========================
st.header("1. Nhập thông tin thu nhập")

with st.form("form_tinh_luong"):
    col1, col2 = st.columns(2)

    with col1:
        luong_co_ban = st.number_input(
            "Lương cơ bản (triệu đồng)",
            min_value=0.0,
            value=10.0,
            step=0.5,
            format="%.3f"
        )

        tien_thuong = st.number_input(
            "Tiền thưởng (triệu đồng)",
            min_value=0.0,
            value=1.0,
            step=0.5,
            format="%.3f"
        )

        phu_cap_co_bhxh = st.number_input(
            "Phụ cấp có tính BHXH (triệu đồng)",
            min_value=0.0,
            value=1.0,
            step=0.5,
            format="%.3f"
        )

    with col2:
        phu_cap_khong_bhxh = st.number_input(
            "Phụ cấp không tính BHXH (triệu đồng)",
            min_value=0.0,
            value=0.5,
            step=0.5,
            format="%.3f"
        )

        so_nguoi_phu_thuoc = st.number_input(
            "Số người phụ thuộc",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )

    submitted = st.form_submit_button(
        "🧮 TÍNH THUẾ VÀ LƯƠNG THỰC LÃNH",
        use_container_width=True,
        type="primary"
    )

# =========================
# TÍNH TOÁN VÀ HIỂN THỊ
# =========================
if submitted:
    # 1. Tổng thu nhập
    tong_thu_nhap = (
        luong_co_ban
        + tien_thuong
        + phu_cap_co_bhxh
        + phu_cap_khong_bhxh
    )

    # 2. Khoản bảo hiểm người lao động đóng theo giả định của code gốc
    tien_dong_bhxh = (
        luong_co_ban + phu_cap_co_bhxh
    ) * 0.105

    # 3. Thu nhập tính thuế theo mức giảm trừ trong code gốc
    giam_tru_ban_than = 15.5
    giam_tru_nguoi_phu_thuoc = 6.2 * so_nguoi_phu_thuoc

    thu_nhap_tinh_thue = (
        tong_thu_nhap
        - giam_tru_ban_than
        - giam_tru_nguoi_phu_thuoc
        - tien_dong_bhxh
    )

    # 4. Thuế TNCN
    thue_tncn = tinh_thue_tncn(thu_nhap_tinh_thue)

    # 5. Tiền thực lãnh
    thuc_lanh = tong_thu_nhap - tien_dong_bhxh - thue_tncn

    # =========================
    # KẾT QUẢ TỔNG QUAN
    # =========================
    st.divider()
    st.header("2. Kết quả tính toán")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Tổng thu nhập",
            value=f"{dinh_dang_tien(tong_thu_nhap)} triệu đồng"
        )

    with col2:
        st.metric(
            label="Thuế TNCN phải nộp",
            value=f"{dinh_dang_tien(thue_tncn)} triệu đồng"
        )

    with col3:
        st.metric(
            label="💵 TIỀN THỰC LÃNH",
            value=f"{dinh_dang_tien(thuc_lanh)} triệu đồng"
        )

    # =========================
    # CHI TIẾT CÁC KHOẢN
    # =========================
    st.header("3. Bảng chi tiết thu nhập và khấu trừ")

    du_lieu = [
        ["Lương cơ bản", luong_co_ban],
        ["Tiền thưởng", tien_thuong],
        ["Phụ cấp có tính BHXH", phu_cap_co_bhxh],
        ["Phụ cấp không tính BHXH", phu_cap_khong_bhxh],
        ["TỔNG THU NHẬP", tong_thu_nhap],
        ["Giảm trừ bản thân (theo code gốc)", giam_tru_ban_than],
        ["Giảm trừ người phụ thuộc", giam_tru_nguoi_phu_thuoc],
        ["Tiền đóng BHXH, BHYT, BHTN (10,5%)", tien_dong_bhxh],
        ["Thu nhập tính thuế trước khi áp dụng mức sàn", thu_nhap_tinh_thue],
        ["Thu nhập tính thuế áp dụng biểu thuế", max(0, thu_nhap_tinh_thue)],
        ["Thuế TNCN", thue_tncn],
        ["TIỀN THỰC LÃNH", thuc_lanh],
    ]

    bang_ket_qua = pd.DataFrame(
        du_lieu,
        columns=["Nội dung", "Số tiền (triệu đồng)"]
    )

    bang_hien_thi = bang_ket_qua.copy()
    bang_hien_thi["Số tiền (triệu đồng)"] = (
        bang_hien_thi["Số tiền (triệu đồng)"].map(dinh_dang_tien)
    )

    st.dataframe(
        bang_hien_thi,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # BIỂU ĐỒ PHÂN BỔ
    # =========================
    st.header("4. Biểu đồ phân bổ thu nhập")

    bieu_do = pd.DataFrame({
        "Khoản mục": [
            "Tiền thực lãnh",
            "Tiền đóng bảo hiểm",
            "Thuế TNCN"
        ],
        "Số tiền (triệu đồng)": [
            thuc_lanh,
            tien_dong_bhxh,
            thue_tncn
        ]
    })

    st.bar_chart(
        bieu_do.set_index("Khoản mục"),
        y="Số tiền (triệu đồng)"
    )

    # =========================
    # TẢI KẾT QUẢ
    # =========================
    st.header("5. Xuất kết quả")

    csv_data = bang_ket_qua.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 Tải bảng tính về máy (CSV)",
        data=csv_data,
        file_name="ket_qua_tinh_luong.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.success(
        f"Đã tính xong! Tiền thực lãnh theo các giả định trên là "
        f"{dinh_dang_tien(thuc_lanh)} triệu đồng/tháng."
    )

    st.info(
        "Lưu ý: Đây là kết quả tính toán tham khảo theo công thức đã nhập. "
        "Khi áp dụng thực tế, cần xác định đúng các khoản thu nhập chịu thuế, "
        "mức giảm trừ, căn cứ đóng bảo hiểm và biểu thuế áp dụng cho kỳ lương."
    )
else:
    st.info(
        "Vui lòng nhập thông tin thu nhập, sau đó nhấn nút "
        "'TÍNH THUẾ VÀ LƯƠNG THỰC LÃNH' để xem kết quả."
    )

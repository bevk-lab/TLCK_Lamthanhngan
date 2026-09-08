import streamlit as st
import pandas as pd

# Cấu hình trang Streamlit (Giao diện rộng - Wide Mode)
st.set_page_config(
    page_title="Pokedex Big Data Analytics Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh giao diện sang trọng, sạch sẽ và dễ nhìn số liệu
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)


# Tải dữ liệu đã qua xử lý (Định dạng sạch từ PySpark)
@st.cache_data
def load_data():
    return pd.read_csv("pokemon_clean.csv")


df = load_data()

# --- TIÊU ĐỀ TRANG ---
st.markdown('<p class="main-header">⚡ Pokedex Big Data Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Hệ thống phân tích dữ liệu lớn Pokemon xử lý phân tán bằng <b>PySpark</b> trên Google Colab và trực quan hóa qua <b>Streamlit</b>[cite: 1, 6].</p>',
    unsafe_allow_html=True)

# --- THANH BÊN (SIDEBAR) - BỘ LỌC TƯƠNG TÁC ---
st.sidebar.header("🎛️ Bảng điều khiển & Bộ lọc")
st.sidebar.markdown("---")

# Bộ lọc Hệ chính (Type 1)
type_list = ["Tất cả"] + sorted(df['type_1'].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("🎯 Chọn Hệ chính (Type 1):", options=type_list)

# Bộ lọc Thế hệ (Generation)
if 'generation' in df.columns:
    gen_list = ["Tất cả"] + sorted(df['generation'].dropna().unique().tolist())
    selected_gen = st.sidebar.selectbox("🌐 Chọn Thế hệ (Generation):", options=gen_list)
else:
    selected_gen = "Tất cả"

# Lọc dữ liệu theo lựa chọn của người dùng
filtered_df = df.copy()
if selected_type != "Tất cả":
    filtered_df = filtered_df[filtered_df['type_1'] == selected_type]
if selected_gen != "Tất cả":
    filtered_df = filtered_df[filtered_df['generation'] == selected_gen]

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Gợi ý:** Dữ liệu nguồn đã được làm sạch qua hệ thống PySpark, loại bỏ các bản ghi lỗi và tối ưu hóa tốc độ truy vấn[cite: 1, 3].")

# --- KHU VỰC CHÍNH: HIỂN THỊ CÁC THẺ CHỈ SỐ (KPI METRICS) ---
col1, col2, col3, col4 = st.columns(4)

total_pokemons = len(filtered_df)

# Tính toán các chỉ số thống kê cơ bản
if 'total' in filtered_df.columns:
    avg_total = filtered_df['total'].mean() if total_pokemons > 0 else 0
    max_pokemon = filtered_df.loc[filtered_df['total'].idxmax()][
        'name'] if total_pokemons > 0 and not filtered_df.empty else "N/A"
else:
    filtered_df['calculated_total'] = filtered_df[['hp', 'attack', 'defense', 'speed']].sum(axis=1)
    avg_total = filtered_df['calculated_total'].mean() if total_pokemons > 0 else 0
    max_pokemon = filtered_df.loc[filtered_df['calculated_total'].idxmax()][
        'name'] if total_pokemons > 0 and not filtered_df.empty else "N/A"

legendary_count = filtered_df['legendary'].sum() if 'legendary' in filtered_df.columns else 0

with col1:
    st.metric(label="📊 Tổng số Pokemon", value=f"{total_pokemons:,}")
with col2:
    st.metric(label="⭐ Điểm Sức mạnh TB", value=f"{avg_total:.1f}")
with col3:
    st.metric(label="👑 Pokemon Mạnh Nhất", value=str(max_pokemon))
with col4:
    st.metric(label="✨ Số lượng Huyền thoại", value=f"{legendary_count:,}")

st.markdown("---")

# --- PHÂN CHIA NỘI DUNG THÀNH CÁC TAB KHOA HỌC ---
tab1, tab2, tab3 = st.tabs(
    ["📈 Biểu đồ Phân tích & Xếp hạng", "📋 Danh sách Chi tiết Dữ liệu", "🏛️ Báo cáo Kiến trúc Big Data"])

with tab1:
    if selected_gen != "Tất cả":
        st.subheader(f"🏆 Xếp hạng Sức mạnh Tổng quan theo Hệ (Thế hệ: {selected_gen})")
    else:
        st.subheader("🏆 Xếp hạng Sức mạnh Tổng quan theo Hệ (Tất cả các Thế hệ)")

    st.markdown(
        "Biểu đồ cột thể hiện điểm sức mạnh trung bình của từng hệ Pokemon, tự động thay đổi theo **Thế hệ (Generation)** bạn chọn ở thanh bên.")

    # Lọc dữ liệu riêng cho biểu đồ dựa trên Thế hệ (Generation) được chọn ở sidebar
    if selected_gen != "Tất cả":
        chart_df = df[df['generation'] == selected_gen]
    else:
        chart_df = df

    if not chart_df.empty:
        # Xác định cột tính tổng sức mạnh
        val_col = 'total' if 'total' in chart_df.columns else (
            'calculated_total' if 'calculated_total' in chart_df.columns else 'attack')

        # Gom nhóm theo type_1 dựa trên dữ liệu đã lọc theo thế hệ
        type_avg = chart_df.groupby('type_1')[val_col].mean().reset_index()
        type_avg = type_avg.sort_values(by=val_col, ascending=False)

        # Hiển thị biểu đồ cột trực quan
        chart_data = type_avg.set_index('type_1')[val_col]
        st.bar_chart(chart_data)
    else:
        st.warning("Không tìm thấy dữ liệu phù hợp với thế hệ này.")

with tab2:
    st.subheader("📋 Bảng Dữ liệu Sạch Đã Xử lý")
    st.markdown(
        "Danh sách chi tiết các chỉ số định danh và sức mạnh của Pokemon sau khi đi qua pipeline xử lý dữ liệu lớn.")

    # Lựa chọn các cột hiển thị đẹp mắt
    display_columns = [col for col in
                       ['name', 'type_1', 'type_2', 'generation', 'hp', 'attack', 'defense', 'speed', 'total'] if
                       col in filtered_df.columns]
    if not display_columns:
        display_columns = filtered_df.columns.tolist()

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("🏛️ Tài liệu Minh chứng Kiến trúc Kỹ thuật Big Data")
    st.markdown("""
    Ứng dụng này được xây dựng bám sát mô hình kiến trúc phân lớp hiện đại trong các tài liệu chuyên ngành:
    1. **Tầng Ingestion & Processing (Xử lý phân tán):** Dữ liệu thô từ Kaggle được nạp, kiểm tra chất lượng (Data Quality) và biến đổi thông qua **PySpark DataFrame API** trên môi trường Google Colab[cite: 1, 6].
    2. **Tầng Storage (Lưu trữ tối ưu):** Dữ liệu sạch được xuất ra định dạng cột chuẩn **Parquet**, giúp tối ưu hóa không gian lưu trữ và tăng tốc độ truy vấn đọc[cite: 3, 5, 6].
    3. **Tầng Consumption (Tiêu thụ dữ liệu):** Giao diện **Streamlit** đóng vai trò là lớp trực quan hóa cuối cùng để phục vụ việc ra quyết định quản trị[cite: 6].
    """)

    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.success(f"✅ **Trạng thái dữ liệu:** Đã chuẩn hóa thành công `{len(df):,}` bản ghi sạch.")
    with col_info2:
        st.info("⚡ **Công nghệ cốt lõi:** PySpark + Parquet + Streamlit Cloud.")
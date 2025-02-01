import streamlit as st
import pandas as pd
from datetime import datetime

# Fungsi untuk menghitung penyusutan
def calculate_depreciation(initial_cost, acquisition_year, useful_life, reporting_year, capitalizations=None):
    if capitalizations is None:
        capitalizations = []
    
    cap_dict = {}
    for cap in capitalizations:
        year = cap['year']
        cap_dict.setdefault(year, []).append(cap)
    
    book_value = initial_cost
    remaining_life = useful_life
    current_year = acquisition_year
    original_life = useful_life
    accumulated_dep = 0
    schedule = []
    
    while remaining_life > 0 and current_year <= reporting_year:
        if current_year in cap_dict:
            for cap in cap_dict[current_year]:
                if cap['year'] > reporting_year:
                    continue
                book_value += cap['amount']
                life_extension = cap.get('life_extension', 0)
                remaining_life = min(remaining_life + life_extension, original_life)
        
        annual_dep = book_value / remaining_life if remaining_life > 0 else 0
        accumulated_dep += annual_dep
        
        schedule.append({
            'year': current_year,
            'depreciation': round(annual_dep, 2),
            'accumulated': round(accumulated_dep, 2),
            'book_value': round(book_value - annual_dep, 2),
            'sisa_mm': remaining_life - 1  # Kolom baru untuk sisa masa manfaat
        })
        
        book_value -= annual_dep
        remaining_life -= 1
        current_year += 1
    
    return schedule

# Streamlit app
st.title("Shz_Depre_Tahunan")

# Input Parameter
st.sidebar.header("🔢 Parameter Input")
initial_cost = st.sidebar.number_input("Initial Cost (Rp)", min_value=0.0, step=0.01, format="%.2f")
acquisition_year = st.sidebar.number_input("Tahun Perolehan", min_value=1900, max_value=datetime.now().year, step=1)
useful_life = st.sidebar.number_input("Masa Manfaat (tahun)", min_value=1, step=1)
reporting_year = st.sidebar.number_input("Tahun Pelaporan", min_value=1900, max_value=datetime.now().year, step=1)

# Kapitalisasi
st.sidebar.header("📊 Daftar Kapitalisasi")
capitalizations = []
if "capitalizations" not in st.session_state:
    st.session_state.capitalizations = []

def add_capitalization():
    year = st.session_state.cap_year
    amount = st.session_state.cap_amount
    life_extension = st.session_state.cap_life_extension
    st.session_state.capitalizations.append({
        'year': year,
        'amount': amount,
        'life_extension': life_extension
    })

def edit_capitalization(index):
    st.session_state.cap_year = st.session_state.capitalizations[index]['year']
    st.session_state.cap_amount = st.session_state.capitalizations[index]['amount']
    st.session_state.cap_life_extension = st.session_state.capitalizations[index]['life_extension']
    st.session_state.edit_index = index

def save_edited_capitalization():
    index = st.session_state.edit_index
    st.session_state.capitalizations[index] = {
        'year': st.session_state.cap_year,
        'amount': st.session_state.cap_amount,
        'life_extension': st.session_state.cap_life_extension
    }
    st.session_state.edit_index = None

st.sidebar.number_input("Tahun Kapitalisasi", key="cap_year", min_value=1900, max_value=datetime.now().year, step=1)
st.sidebar.number_input("Jumlah Kapitalisasi (Rp)", key="cap_amount", min_value=0.0, step=0.01, format="%.2f")
st.sidebar.number_input("Tambah Usia (tahun)", key="cap_life_extension", min_value=0, step=1)

if "edit_index" in st.session_state and st.session_state.edit_index is not None:
    st.sidebar.button("💾 Simpan Perubahan", on_click=save_edited_capitalization)
else:
    st.sidebar.button("➕ Tambah Kapitalisasi", on_click=add_capitalization)

# Tampilkan kapitalisasi yang telah ditambahkan
st.sidebar.subheader("Kapitalisasi yang Ditambahkan")
for i, cap in enumerate(st.session_state.capitalizations):
    st.sidebar.write(f"Tahun: {cap['year']}, Jumlah: Rp{cap['amount']:,.2f}, Tambah Usia: {cap['life_extension']} tahun")
    st.sidebar.button("✏️ Edit", key=f"edit_{i}", on_click=edit_capitalization, args=(i,))

# Tombol untuk menghitung penyusutan
if st.sidebar.button("🔍 Hitung Penyusutan"):
    if initial_cost > 0 and acquisition_year <= reporting_year and useful_life > 0:
        schedule = calculate_depreciation(
            initial_cost=initial_cost,
            acquisition_year=acquisition_year,
            useful_life=useful_life,
            reporting_year=reporting_year,
            capitalizations=st.session_state.capitalizations
        )
        
        # Tampilkan hasil perhitungan
        st.subheader("📈 Hasil Perhitungan")
        df = pd.DataFrame(schedule)
        st.dataframe(df)
        
        # Tombol untuk mengekspor ke Excel
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')
        
        csv = convert_df(df)
        st.download_button(
            label="📥 Export ke Excel",
            data=csv,
            file_name='depreciation_schedule.csv',
            mime='text/csv',
        )
    else:
        st.error("Pastikan semua input valid dan lengkap.")

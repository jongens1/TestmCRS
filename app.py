import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="Alza Pick Test", page_icon="📦")

# Inicializácia session state (pamäť aplikácie)
if 'picking_list' not in st.session_state:
    st.session_state.picking_list = []
    st.session_state.current_index = 0
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.test_active = False

st.title("📦 Picking Speed Test")

# --- OBRAZOVKA 1: NASTAVENIE ---
if not st.session_state.test_active and st.session_state.end_time is None:
    st.write("Vložte zoznam produktov (Formát: Kód, EAN, Počet)")
    data_input = st.text_area("Vstup dát", placeholder="A123, 859123456789, 3\nB456, 859987654321, 2", height=200)
    
    if st.button("🚀 Spustiť test"):
        if data_input:
            lines = data_input.strip().split('\n')
            temp_list = []
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 3:
                    try:
                        code = parts[0].strip()
                        ean = parts[1].strip()
                        qty = int(parts[2].strip())
                        # Rozmnoženie na jednotlivé kusy
                        for _ in range(qty):
                            temp_list.append({"code": code, "ean": ean})
                    except ValueError:
                        continue
            
            if temp_list:
                random.shuffle(temp_list)
                st.session_state.picking_list = temp_list
                st.session_state.current_index = 0
                st.session_state.test_active = True
                st.session_state.start_time = time.time()
                st.rerun()
        else:
            st.error("Prosím, vložte nejaké dáta.")

# --- OBRAZOVKA 2: TEST ---
elif st.session_state.test_active:
    idx = st.session_state.current_index
    total = len(st.session_state.picking_list)
    
    if idx < total:
        item = st.session_state.picking_list[idx]
        
        # Priebeh
        st.progress((idx) / total)
        st.subheader(f"Položka {idx + 1} z {total}")
        
        # Zobrazenie produktu
        st.metric("Kód produktu", item['code'])
        st.info(f"EAN: {item['ean']}")
        
        st.write("---")
        # Tlačidlo pre ďalší kus
        if st.button("✅ NASKENOVANÉ (Next)", use_container_width=True):
            st.session_state.current_index += 1
            if st.session_state.current_index >= total:
                st.session_state.end_time = time.time()
                st.session_state.test_active = False
            st.rerun()
            
    if st.button("❌ Zrušiť test"):
        st.session_state.test_active = False
        st.session_state.picking_list = []
        st.session_state.end_time = None
        st.rerun()

# --- OBRAZOVKA 3: VÝSLEDKY ---
elif st.session_state.end_time is not None:
    duration = st.session_state.end_time - st.session_state.start_time
    total_items = len(st.session_state.picking_list)
    avg_time = duration / total_items
    
    st.balloons()
    st.success("Test dokončený!")
    
    col1, col2 = st.columns(2)
    col1.metric("Celkový čas", f"{duration:.2f} s")
    col2.metric("Priemer na kus", f"{avg_time:.2f} s")
    
    if st.button("🔄 Nový test"):
        st.session_state.end_time = None
        st.session_state.picking_list = []
        st.session_state.test_active = False
        st.rerun()

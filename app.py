import streamlit as st
from st_supabase_connection import SupabaseConnection

# 1. Configuración de la página
st.set_page_config(page_title="Mis Finanzas", page_icon="📊", layout="centered")

# 2. Estilo CSS para mejorar la apariencia
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
        background-color: #007bff; 
        color: white; 
        font-weight: bold;
        border: none;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Mis Finanzas")
st.write("Gestiona tus finanzas desde Telegram y visualiza tus reportes aquí.")

# 3. Inicializar conexión con Supabase
conn = st.connection("supabase", type=SupabaseConnection)

# 4. Formulario de acceso
email_usuario = st.text_input("📧 Introduce tu correo electrónico para ver tus datos:")

if email_usuario:
    try:
        # Buscar el perfil del usuario en la tabla 'profiles'
        res_perfil = conn.client.table("profiles").select("*").eq("email", email_usuario).execute()
        
        if res_perfil.data:
            user = res_perfil.data[0]
            st.subheader(f"👋 ¡Hola, {user.get('full_name', 'Usuario')}!")
            
            # --- SECCIÓN VÍNCULO TELEGRAM ---
            with st.expander("🔗 Vincular con Telegram (Configuración de Cédula)"):
                st.info("El número que pongas aquí es el que deberás decirle al bot de Telegram.")
                cedula_actual = user.get('cedula', '')
                nueva_cedula = st.text_input("Tu número de Cédula/ID:", value=cedula_actual)
                
                if st.button("Guardar Cédula"):
                    conn.client.table("profiles").update({"cedula": nueva_cedula}).eq("id", user['id']).execute()
                    st.success("✅ ¡Cédula actualizada! Ya puedes usar el bot con este número.")
                    st.rerun()

            # --- TABLA DE MOVIMIENTOS ---
            st.divider()
            st.subheader("💰 Tus Movimientos Recientes")
            
            # Traer transacciones vinculadas al UUID del usuario
            res_trans = conn.client.table("transacciones").select("*").eq("user_id", user['id']).order("created_at", desc=True).execute()
            
            if res_trans.data:
                # Mostrar tabla de datos
                st.dataframe(res_trans.data, use_container_width=True, hide_index=True)
                
                # Cálculos de totales
                total_egresos = sum(item['monto'] for item in res_trans.data if item['tipo'] == 'Egreso')
                total_ingresos = sum(item['monto'] for item in res_trans.data if item['tipo'] == 'Ingreso')
                balance = total_ingresos - total_egresos
                
                # Mostrar métricas visuales
                col1, col2, col3 = st.columns(3)
                col1.metric("Ingresos", f"${total_ingresos:,}", delta_color="normal")
                col2.metric("Egresos", f"${total_egresos:,}", delta="-", delta_color="inverse")
                col3.metric("Balance", f"${balance:,}")
            else:
                st.warning("Aún no tienes movimientos registrados. ¡Prueba registrando algo en el bot!")
                
        else:
            st.error("❌ No encontramos una cuenta con ese correo. Verifica que sea el mismo con el que te registraste.")
            
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        st.info("Asegúrate de haber activado las políticas RLS en Supabase para la tabla 'profiles'.")

# Pie de página
st.sidebar.markdown("---")
st.sidebar.write("🚀 Desarrollado por Lexilis")
st.sidebar.info("Usa este panel para monitorear tus gastos diarios sincronizados con Telegram.")

import streamlit as st
from st_supabase_connection import SupabaseConnection

# Configuración visual
st.set_page_config(page_title="Mis Finanzas", page_icon="📊")

# Estilo personalizado para que se vea genial
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Mis Finanzas")
st.write("Gestiona tus ingresos y egresos desde Telegram y visualízalos aquí.")

# Conexión con Supabase (los datos sensibles los pondremos en el siguiente paso)
conn = st.connection("supabase", type=SupabaseConnection)

# Formulario de entrada
email_usuario = st.text_input("📧 Introduce tu correo electrónico para ver tus datos:")

if email_usuario:
    # 1. Buscar el perfil (Cambio de sintaxis aquí)
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
                st.success("¡Cédula actualizada! Ya puedes ir al bot.")
                st.rerun()

        # --- TABLA DE MOVIMIENTOS ---
        st.divider()
        st.subheader("💰 Tus Movimientos Recientes")
        
        # Traer transacciones (Cambio de sintaxis aquí)
        res_trans = conn.client.table("transacciones").select("*").eq("user_id", user['id']).order("created_at", desc=True).execute()
        
        if res_trans.data:
            st.dataframe(res_trans.data, use_container_width=True, hide_index=True)
            # ... el resto del código de los totales sigue igual ...
        
        if res_trans.data:
            # Mostrar tabla bonita
            st.dataframe(res_trans.data, use_container_width=True, hide_index=True)
            
            # Un pequeño resumen rápido
            total_egresos = sum(item['monto'] for item in res_trans.data if item['tipo'] == 'Egreso')
            total_ingresos = sum(item['monto'] for item in res_trans.data if item['tipo'] == 'Ingreso')
            
            col1, col2 = st.columns(2)
            col1.metric("Total Ingresos", f"${total_ingresos:,}")
            col2.metric("Total Egresos", f"${total_egresos:,}")
        else:
            st.warning("Aún no tienes movimientos registrados. ¡Escríbele al bot!")
            
    else:
        st.error("No encontramos una cuenta con ese correo. Asegúrate de haber iniciado sesión con Google en la base de datos.")

st.sidebar.markdown("---")
st.sidebar.write("🚀 Desarrollado por Lexilis")

import pandas as pd
from faker import Faker
import random
import os

def main():
    # Inicializamos Faker con la configuración regional de Colombia
    fake = Faker('es_CO')
    
    print("=========================================================")
    print("  🛠️  GENERADOR DE DATOS MOCK - IA TEAM SPRINT")
    print("=========================================================")
    print("Seleccione el conjunto de datos que necesita generar:")
    print("1. [Proyecto 1] Tickets de Soporte IT (Excel)")
    print("2. [Proyecto 3] Políticas y Contratos Internos (HTML con mucho texto)")
    print("3. [Proyecto 4] Facturas y Comprobantes (Excel)")
    print("4. Generar todos los anteriores")
    print("0. Salir")
    
    opcion = input("\nIngrese una opción (0-4): ")
    
    if opcion == '0':
        print("Saliendo del generador...")
        return
        
    try:
        cantidad = int(input("¿Cuántos registros/documentos desea generar? (Ej. 50): "))
    except ValueError:
        print("Error: Ingrese un número válido. Operación cancelada.")
        return

    # Crear carpeta principal y subcarpetas para la salida
    os.makedirs('mock_output', exist_ok=True)
    
    # ---------------------------------------------------------
    # CONTEXTO SIMULADO PARA AÑADIR REALISMO AL DATASET
    # ---------------------------------------------------------
    tech_issues = [
        "El endpoint de FastAPI devuelve error 500 en producción", 
        "Problema de re-dirección y reglas de caché en Cloudflare", 
        "Despliegue atascado o en crash loop dentro de Railway", 
        "Error de renderizado hidratando componentes en Next.js", 
        "Clases de Tailwind CSS no compilan en la build de producción", 
        "Fallo de timeout en script de limpieza de datos con Pandas", 
        "Error de migración de modelos con Django ORM", 
        "Servidor de Streamlit se cae tras cargar un dataset pesado", 
        "Pérdida de estado en el store de Vue.js"
    ]
    
    proveedores = [
        "Novaventa S.A.S", "Crepes & Waffles Eventos", "Riomotos Mantenimiento", 
        "Prodesa Constructora", "Madecentro", "Librería Nacional", 
        "Rappi Corporativo", "Cloudflare Inc.", "Railway App", "Amazon Web Services"
    ]

    # =========================================================
    # GENERADOR P1: TICKETS DE SOPORTE (EXCEL)
    # =========================================================
    if opcion in ['1', '4']:
        print(f"\nGenerando {cantidad} tickets de soporte técnico...")
        data_tickets = []
        for _ in range(cantidad):
            data_tickets.append({
                "ID_Ticket": f"TCK-{fake.unique.random_int(min=10000, max=99999)}",
                "Fecha_Reporte": fake.date_time_between(start_date='-60d', end_date='now').strftime("%Y-%m-%d %H:%M"),
                "Usuario_Afectado": fake.name(),
                "Departamento": random.choice(["Ventas", "Operaciones", "Desarrollo", "Recursos Humanos", "Finanzas"]),
                "Asunto": random.choice(tech_issues) if random.random() > 0.4 else fake.sentence(nb_words=7),
                "Descripcion_Detallada": fake.text(max_nb_chars=1200),  # Mucho texto para estresar el LLM
                "Nivel_Urgencia_Usuario": random.choice(["Bajo", "Normal", "Alto", "Crítico", "Crítico"]),
                "Estado_Actual": random.choice(["Pendiente", "Investigando", "Escalado", "Resuelto"])
            })
        df_tickets = pd.DataFrame(data_tickets)
        df_tickets.to_excel('mock_output/P1_Tickets_Soporte.xlsx', index=False)
        print("✅ Generado: mock_output/P1_Tickets_Soporte.xlsx")

    # =========================================================
    # GENERADOR P3: CONTRATOS Y POLÍTICAS (HTML)
    # =========================================================
    if opcion in ['2', '4']:
        print(f"\nGenerando {cantidad} documentos de políticas internas en HTML...")
        os.makedirs('mock_output/Documentos_HTML', exist_ok=True)
        
        # 3 Diseños diferentes para simular la vida real (distintos layouts afectan cómo extrae texto el modelo)
        templates_html = [
            # Plantilla 1: Legal Clásico (Serif, denso, justificado)
            '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title><style>body { font-family: 'Times New Roman', serif; margin: 40px; background-color: #fdfbf7; color: #111; line-height: 1.6; } h1 { text-align: center; border-bottom: 3px double #000; padding-bottom: 10px; text-transform: uppercase; } h2 { color: #333; margin-top: 30px; font-style: italic; } p { text-align: justify; margin-bottom: 15px; } .footer { font-size: 0.8em; text-align: center; margin-top: 50px; border-top: 1px solid #ccc; padding-top: 10px; }</style></head><body><h1>{title}</h1>{content}<div class="footer">Documento Oficial - Uso Estrictamente Confidencial</div></body></html>''',
            
            # Plantilla 2: Corporativo Moderno (Sans-serif, tarjetas, limpio)
            '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title><style>body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background-color: #f4f7f6; color: #2c3e50; line-height: 1.8; } .container { max-width: 850px; margin: 40px auto; background: #fff; padding: 50px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); } h1 { color: #2980b9; border-left: 6px solid #2980b9; padding-left: 15px; } h2 { color: #34495e; border-bottom: 1px solid #eaeaea; padding-bottom: 8px; margin-top: 40px; } p { margin-bottom: 20px; color: #555; }</style></head><body><div class="container"><h1>{title}</h1>{content}</div></body></html>''',
            
            # Plantilla 3: Manual Técnico/Operativo (Monoespaciado, listas indentadas)
            '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title><style>body { font-family: 'Courier New', Courier, monospace; margin: 50px; background-color: #fff; color: #000; line-height: 1.5; } h1 { text-align: center; letter-spacing: 2px; background-color: #000; color: #fff; padding: 10px; } h2 { text-decoration: underline; margin-top: 40px; } p { text-align: justify; text-indent: 30px; } .clause { margin-bottom: 25px; }</style></head><body><h1>{title}</h1><div style="margin-top: 30px;">{content}</div></body></html>'''
        ]
        
        nombres_doc = ["Manual de Convivencia - Conjunto Residencial Armonía", "Acuerdo de Confidencialidad y NDA", "Política de Trabajo Remoto e Infraestructura", "Manual de Arquitectura Cloud", "Términos de Contratación de Proveedores"]
        
        for i in range(cantidad):
            title = random.choice(nombres_doc) if i < len(nombres_doc) else fake.sentence(nb_words=6).replace('.', '').upper()
            
            # Generar mucho texto (entre 6 y 15 cláusulas densas)
            paragraphs = []
            for j in range(random.randint(6, 15)):
                paragraphs.append(f"<div class='clause'><h2>Cláusula {j+1}: {fake.sentence(nb_words=5).replace('.','')}</h2><p>{fake.text(max_nb_chars=2000)}</p><p>{fake.text(max_nb_chars=1800)}</p></div>")
            
            content = "".join(paragraphs)
            html = templates_html[i % 3].format(title=title, content=content)
            
            nombre_archivo = f'mock_output/Documentos_HTML/Doc_{i+1}_{title[:20].replace(" ", "_")}.html'
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write(html)
                
        print(f"✅ Generado: {cantidad} archivos HTML en mock_output/Documentos_HTML/")

    # =========================================================
    # GENERADOR P4: FACTURAS / DATOS FINANCIEROS (EXCEL)
    # =========================================================
    if opcion in ['3', '4']:
        print(f"\nGenerando {cantidad} registros de facturación financiera...")
        data_facturas = []
        for _ in range(cantidad):
            subtotal = round(random.uniform(150000, 15000000), 2)
            impuesto_iva = round(subtotal * 0.19, 2) # IVA 19% Colombia
            
            data_facturas.append({
                "Numero_Factura": f"FE-{fake.unique.random_int(min=100000, max=999999)}",
                "Fecha_Emision": fake.date_between(start_date='-1y', end_date='today').strftime("%Y-%m-%d"),
                "Entidad_Razon_Social": random.choice(proveedores) if random.random() > 0.3 else fake.company(),
                "NIT_Proveedor": f"{fake.random_int(min=800000000, max=999999999)}-{random.randint(0,9)}",
                "Concepto_Operacion": fake.catch_phrase(),
                "Subtotal_Base_COP": subtotal,
                "Impuesto_IVA_COP": impuesto_iva,
                "Total_Factura_COP": subtotal + impuesto_iva,
                "Moneda": "COP",
                "Estado_Reconciliacion": random.choice(["Pendiente", "Procesado", "Rechazado", "Pagado", "Discrepancia detectada"])
            })
        df_facturas = pd.DataFrame(data_facturas)
        df_facturas.to_excel('mock_output/P4_Facturas_Finanzas.xlsx', index=False)
        print("✅ Generado: mock_output/P4_Facturas_Finanzas.xlsx")

    print("\n🚀 ¡Generación de entorno de pruebas completada exitosamente!")

if __name__ == "__main__":
    main()
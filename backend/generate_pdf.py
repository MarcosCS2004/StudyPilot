from fpdf import FPDF

def create_test_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Apuntes de Prueba: Historia de la IA", ln=True, align='C')
    
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=12)
    
    content = [
        "El termino Inteligencia Artificial fue acuñado por John McCarthy en 1956 durante la conferencia de Dartmouth.",
        "Uno de los hitos mas importantes fue la creacion de ELIZA por Joseph Weizenbaum en los años 60, el primer chatbot.",
        "En los años 90, Deep Blue de IBM vencio a Garry Kasparov en ajedrez, demostrando el poder de la computacion.",
        "Actualmente, los modelos de lenguaje como GPT-4 utilizan arquitecturas Transformer para procesar informacion.",
        "El aprendizaje supervisado requiere datos etiquetados, mientras que el no supervisado busca patrones en datos brutos."
    ]
    
    for line in content:
        pdf.multi_cell(0, 10, txt=line)
        pdf.ln(2)
        
    pdf.output("../Apuntes_IA_Prueba.pdf")
    print("PDF creado con exito en la raiz del proyecto: Apuntes_IA_Prueba.pdf")

if __name__ == "__main__":
    create_test_pdf()

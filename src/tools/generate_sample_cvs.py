from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_sample_cv(filename, candidate_info):
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750  # Starting y position
    
    # Add content
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, candidate_info['name'])
    y -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Email: {candidate_info['email']}")
    y -= 20
    c.drawString(50, y, f"Teléfono: {candidate_info['phone']}")
    y -= 20
    c.drawString(50, y, f"Ubicación: {candidate_info['location']}")
    y -= 40
    
    # Education
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Educación")
    y -= 25
    c.setFont("Helvetica", 12)
    for edu in candidate_info['education']:
        c.drawString(50, y, edu)
        y -= 20
    y -= 20
    
    # Skills
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Habilidades")
    y -= 25
    c.setFont("Helvetica", 12)
    for skill in candidate_info['skills']:
        c.drawString(50, y, f"• {skill}")
        y -= 20
    y -= 20
    
    # Languages
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Idiomas")
    y -= 25
    c.setFont("Helvetica", 12)
    for lang in candidate_info['languages']:
        c.drawString(50, y, f"• {lang}")
        y -= 20
    
    c.save()

def generate_sample_cvs():
    # Sample candidates for different positions
    candidates = [
        {
            'name': 'Ana García Martínez',
            'email': 'ana.garcia@email.com',
            'phone': '5512345678',
            'location': 'Ciudad de México',
            'education': [
                'Licenciatura en Administración de Empresas - UNAM',
                'Diplomado en Recursos Humanos - ITAM'
            ],
            'skills': [
                'Microsoft Office avanzado',
                'SAP',
                'Gestión de personal',
                'Reclutamiento y selección',
                'Nómina y compensaciones'
            ],
            'languages': [
                'Español nativo',
                'Inglés avanzado'
            ]
        },
        {
            'name': 'Carlos Rodríguez López',
            'email': 'carlos.rodriguez@email.com',
            'phone': '5523456789',
            'location': 'Monterrey, NL',
            'education': [
                'Ingeniería en Sistemas Computacionales - Tec de Monterrey',
                'Certificación AWS Solutions Architect'
            ],
            'skills': [
                'Python',
                'JavaScript',
                'React',
                'Node.js',
                'AWS',
                'Docker'
            ],
            'languages': [
                'Español nativo',
                'Inglés avanzado',
                'Alemán básico'
            ]
        },
        {
            'name': 'María Fernanda Torres',
            'email': 'mf.torres@email.com',
            'phone': '5534567890',
            'location': 'Guadalajara, JAL',
            'education': [
                'Licenciatura en Contaduría Pública - ITESO',
                'Maestría en Finanzas - UP'
            ],
            'skills': [
                'Contabilidad general',
                'Análisis financiero',
                'CONTPAQi',
                'Excel avanzado',
                'Declaraciones fiscales'
            ],
            'languages': [
                'Español nativo',
                'Inglés intermedio'
            ]
        }
    ]
    
    # Create CVs directory if it doesn't exist
    cv_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'curriculums')
    os.makedirs(cv_dir, exist_ok=True)
    
    # Generate CVs
    for candidate in candidates:
        filename = os.path.join(cv_dir, f"CV_{candidate['name'].replace(' ', '_')}.pdf")
        create_sample_cv(filename, candidate)
        print(f"Generated CV for {candidate['name']}")

if __name__ == '__main__':
    generate_sample_cvs()

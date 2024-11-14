import os
import asyncio
from InquirerPy import inquirer
from InquirerPy import get_style
from InquirerPy.base.control import Choice
import google.generativeai as genai
from dotenv import load_dotenv

style = get_style({"questionmark": "#5eff00", "answer": "#ffffff", "pointer": "#5eff00"}, style_override=True)


load_dotenv()

class EmailRewriter:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",                
            }
        )

    async def rewrite_email(self, original_text):
        try:
            chat = self.model.start_chat(history=[
                {
                    "role": "user",
                    "parts": ["Eres un redactor de correo electrónico profesional. Tu tarea es mejorar y formalizar el texto dado, manteniendo su intención original pero mejorando su claridad, profesionalismo y eficacia."]
                },
                {
                    "role": "model",
                    "parts": ["Entendido. Estoy listo para ayudarte a mejorar y formalizar textos de correos electrónicos, manteniendo su intención original mientras mejoro su claridad, profesionalismo y eficacia. ¿Cuál es el texto que deseas que reescriba?"]
                }
            ])

            response = await asyncio.to_thread(
                chat.send_message,
                f"Por favor, reescribe, alarga y mejora el siguiente texto de correo:\n\n{original_text}"
            )
            return response.text
        except Exception as e:
            print(f"Error al procesar el texto: {str(e)}")
            return None

async def email_rewriter_menu():
    try:
        rewriter = EmailRewriter()
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Por favor, configure la variable de entorno GEMINI_API_KEY con su clave de API de Gemini.\nCree un archivo '.env' y dentro ponga GEMINI_API_KEY=Your_Api_Key")
        await inquirer.text(message="Presione Enter para volver al menú principal...").execute_async()
        return

    while True:
        choice = await inquirer.select(
                message="   (Use las flechas ↑↓ para navegar, Enter para seleccionar)\n\n   Seleccione una opción:",
            choices=[
                Choice("rewrite", "Reescribir un email"),
                Choice("exit", "Volver al menú principal")
            ],
            default="rewrite",
            pointer="   >",
            qmark='',
            style=style
        ).execute_async()

        if choice == "exit":
            break
        elif choice == "rewrite":
            original_text = await inquirer.text(
                message="Ingrese el texto del email que desea mejorar:",
                multiline=True
            ).execute_async()

            print("Procesando su email...")
            improved_text = await rewriter.rewrite_email(original_text)

            if improved_text:
                print("Email mejorado:")
                print(improved_text)
            else:
                print("No se pudo procesar el email. Por favor, intente de nuevo.\n")

            await inquirer.text(message="Presione Enter para continuar...").execute_async()

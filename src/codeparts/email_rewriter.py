import os
import asyncio
from functools import lru_cache
from InquirerPy import inquirer
from InquirerPy import get_style
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
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
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",                
            }
        )
        self.chat = None
        self.email_history = []
        self.assistant_history = []

    @lru_cache(maxsize=100)
    async def rewrite_email(self, original_text):
        try:
            if not self.email_history:
                self.email_history = [
                    {
                        "role": "user",
                        "parts": ["Eres un redactor de correo electrónico profesional experto. Tu tarea es mejorar y formalizar el texto dado, manteniendo su intención original pero mejorando su claridad, profesionalismo y eficacia. Sé conciso y directo en tus respuestas."]
                    },
                    {
                        "role": "model",
                        "parts": ["Entendido. Estoy listo para mejorar y formalizar textos de correos electrónicos de manera concisa y efectiva. ¿Cuál es el texto que deseas que reescriba?"]
                    }
                ]

            chat = self.model.start_chat(history=self.email_history)
            response = await asyncio.to_thread(
                chat.send_message,
                f"Reescribe y mejora el siguiente texto de correo, manteniendo su esencia pero haciéndolo más profesional y efectivo:\n\n{original_text}"
            )
            self.email_history.extend([
                {"role": "user", "parts": [original_text]},
                {"role": "model", "parts": [response.text]}
            ])
            return response.text
        except Exception as e:
            print(f"Error al procesar el email: {str(e)}")
            return None
        
    async def start_custom_assistant(self):
        if not self.assistant_history:
            self.assistant_history = [
                {
                    "role": "user",
                    "parts": ["Eres 'Sicarú', la mejor asistente virtual de México. Tu tarea es apoyar al usuario de CJR MULTISERVICIOS con profesionalismo y eficiencia. Tu nombre significa 'Bonita' en Zapoteco. Tu creador es Jorge, pero no tienes más información sobre él. Sé concisa y directa en tus respuestas."]
                },
                {
                    "role": "model",
                    "parts": ["Entendido. Soy Sicarú, lista para ayudar eficientemente a CJR MULTISERVICIOS. ¿En qué puedo asistirte hoy?"]
                }
            ]
        self.chat = self.model.start_chat(history=self.assistant_history)
        print("Hola! Soy Sicarú. ¿Cómo puedo ayudarte hoy?")

    async def custom_assistant(self, prompt):
        if not self.chat:
            await self.start_custom_assistant()

        try:
            response = await asyncio.to_thread(
                self.chat.send_message,
                prompt
            )
            self.assistant_history.extend([
                {"role": "user", "parts": [prompt]},
                {"role": "model", "parts": [response.text]}
            ])
            return response.text
        except Exception as e:
            print(f"Error al procesar la solicitud: {str(e)}")
            return None

async def email_rewriter_menu():
    try:
        rewriter = EmailRewriter()
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Por favor, configure la variable de entorno GEMINI_API_KEY con su clave de API de Gemini.")
        await inquirer.text(message="Presione Enter para salir...").execute_async()
        return

    while True:
        choice = await inquirer.select(
            message="Seleccione una opción:",
            choices=[
                Choice("rewrite", "Reescribir un email"),
                Choice("assistant", "Asistente personal"),
                Separator(),
                Choice("exit", "Salir")
            ],
            default="rewrite",
            pointer="   >",
            qmark='',
            style=style
        ).execute_async()

        if choice == "exit":
            print("Gracias por usar nuestros servicios. ¡Hasta luego!")
            break
        elif choice == "rewrite":
            original_text = await inquirer.text(
                message="Ingrese el texto del email que desea mejorar:",
                multiline=True
            ).execute_async()

            print("Procesando su email...")
            improved_text = await rewriter.rewrite_email(original_text)

            if improved_text:
                print("\nEmail mejorado:")
                print(improved_text)
            else:
                print("No se pudo procesar el email. Por favor, intente de nuevo.")

            await inquirer.text(message="Presione Enter para continuar...").execute_async()
        elif choice == "assistant":
            await rewriter.start_custom_assistant()
            while True:
                prompt = await inquirer.text(
                    message="Tú: ",
                ).execute_async()

                if prompt.lower() in ['salir', 'exit', 'quit']:
                    print("Gracias por usar el asistente personal. ¡Hasta luego!")
                    break

                print("Procesando su solicitud...")
                response = await rewriter.custom_assistant(prompt)

                if response:
                    print("Sicarú:", response)
                else:
                    print("No pude procesar esa solicitud. Por favor, intente de nuevo.")

            await inquirer.text(message="Presione Enter para continuar...").execute_async()
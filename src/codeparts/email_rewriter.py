import os
import asyncio
from openai import AsyncOpenAI
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from system.config import OPENAI_API_KEY

class EmailRewriter:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def rewrite_email(self, original_text):
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un redactor de correo electrónico profesional. Tu tarea es mejorar y formalizar el texto dado, manteniendo su intención original pero mejorando su claridad, profesionalismo y eficacia."},
                    {"role": "user", "content": f"Por favor, re escribe y mejora el siguinte texto de correo:\n\n{original_text}"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error al procesar el texto: {str(e)}")
            return None

async def email_rewriter_menu():
    rewriter = EmailRewriter()

    while True:
        choice = await inquirer.select(
            message="Email Re-writer:",
            choices=[
                Choice("rewrite", "Reescribir un email"),
                Choice("exit", "Volver al menú principal")
            ],
            default="rewrite"
        ).execute_async()

        if choice == "exit":
            break
        elif choice == "rewrite":
            original_text = await inquirer.text(
                message="Ingrese el texto del email que desea mejorar:",
                multiline=True
            ).execute_async()

            print("\nProcesando su email...")
            improved_text = await rewriter.rewrite_email(original_text)

            if improved_text:
                print("\nEmail mejorado:")
                print(improved_text)
            else:
                print("\nNo se pudo procesar el email. Por favor, intente de nuevo.")

            await inquirer.text(message="Presione Enter para continuar...").execute_async()
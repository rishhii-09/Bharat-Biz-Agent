import os
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

from agent import process_message
from invoice_utils import generate_invoice
from database import init_db, save_invoice, get_summary, get_last_invoice

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

# ✅ Initialize Database
init_db()

# 🧠 In-memory storage (only for confirmation flow)
user_sessions = {}


@app.get("/")
def home():
    return {"status": "Bharat Biz Agent is running 🚀"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("Incoming:", data)

    if "message" not in data or "text" not in data["message"]:
        return {"status": "ignored"}

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"]["text"].strip().lower()

    # 👋 GREETING
    if user_text in ["hi", "hello", "hey", "/start"]:
        reply = (
            "Hi 👋 I am *Bharat Biz Agent* 🇮🇳\n\n"
            "Try saying:\n"
            "👉 Ramesh ke naam ₹500 ka invoice bana do\n\n"
            "Commands:\n"
            "/summary - Business stats 📊\n"
            "/lastinvoice - Last invoice details 🧾"
        )
        send_message(chat_id, reply)
        return {"status": "ok"}

    # 📊 SUMMARY COMMAND
    if user_text == "/summary":
        total_invoices, total_revenue = get_summary()

        reply = (
            "📊 *Business Summary*\n\n"
            f"Total Invoices: {total_invoices}\n"
            f"Total Revenue: ₹{total_revenue}"
        )

        send_message(chat_id, reply)
        return {"status": "ok"}

    # 🧾 LAST INVOICE COMMAND
    if user_text == "/lastinvoice":
        last = get_last_invoice()

        if not last:
            reply = "No invoices found yet."
        else:
            invoice_id, customer_name, amount, created_at = last
            reply = (
                "🧾 *Last Invoice Details*\n\n"
                f"Invoice ID: {invoice_id}\n"
                f"Customer: {customer_name}\n"
                f"Amount: ₹{amount}\n"
                f"Date: {created_at}"
            )

        send_message(chat_id, reply)
        return {"status": "ok"}

    # 🤖 AI PROCESSING
    result = process_message(user_text)
    reply = "Sorry, samajh nahi aaya 😅"

    # 🧾 CREATE INVOICE
    if result.get("intent") == "CREATE_INVOICE":
        if not result.get("customer_name") or not result.get("amount"):
            reply = "Customer name ya amount missing hai. Dobara boliye."
        else:
            user_sessions[chat_id] = {
                "customer_name": result["customer_name"],
                "amount": int(result["amount"])
            }

            reply = (
                f"₹{result['amount']} ka invoice "
                f"{result['customer_name']} ke naam pe banau aur bheju?\n"
                "Reply YES or NO"
            )

    # ✅ CONFIRM ACTION
    elif result.get("intent") == "CONFIRM_ACTION":
        if result.get("confirmation") == "YES":
            session = user_sessions.get(chat_id)

            if not session:
                reply = "❌ Koi invoice data nahi mila. Pehle invoice request bhejiye."
            else:
                invoice_id, pdf_path = generate_invoice(
                    customer_name=session["customer_name"],
                    amount=session["amount"]
                )

                # ✅ SAVE TO DATABASE
                save_invoice(
                    invoice_id,
                    session["customer_name"],
                    session["amount"]
                )

                send_document(chat_id, pdf_path)

                reply = (
                    f"✅ Invoice created successfully.\n"
                    f"Invoice ID: {invoice_id}"
                )

                del user_sessions[chat_id]
        else:
            reply = "❌ Action cancelled."

    send_message(chat_id, reply)
    return {"status": "ok"}


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
    )


def send_document(chat_id, file_path):
    with open(file_path, "rb") as f:
        requests.post(
            f"{TELEGRAM_URL}/sendDocument",
            data={"chat_id": chat_id},
            files={"document": f}
        )

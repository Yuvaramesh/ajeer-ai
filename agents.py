"""
agents.py — Ajeer Multi-Agent System (LangGraph)
==================================================
Ajeer is a digital money transfer / remittance platform by Monex International Ltd.
Regulated by FCA (FRN: 510848). Based in London, UK.

Agent Architecture:
  User Query
      │
  Supervisor Agent  ─ classifies intent, routes to specialist
      │
      ├──► FAQ Agent           — platform info, how-to, general questions
      ├──► Transfer Agent      — how to send money, fees, steps, beneficiaries
      ├──► Compliance Agent    — KYC/AML, identity verification, regulations
      ├──► Rewards Agent       — rewards program, lucky draw, chances, prizes
      └──► Support Agent       — complaints, refunds, account issues, contact
"""

from __future__ import annotations
import os
import re
from typing import TypedDict, Literal, Any
from dotenv import load_dotenv

import google.generativeai as genai
from langgraph.graph import StateGraph, END

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)


def _gemini(system: str, user: str, history: list[dict] | None = None) -> str:
    """Call Gemini with a system prompt, optional history, and user message."""
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    chat_history = []
    for h in (history or [])[-6:]:
        role = "user" if h.get("role") == "user" else "model"
        chat_history.append({"role": role, "parts": [h["content"]]})
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(f"{system}\n\n{user}")
    return response.text.strip()


# ─────────────────────────────────────────────────────────────────
# Shared Graph State
# ─────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    user_message: str
    history: list[dict]
    user_name: str
    user_country: str
    currency_code: str
    currency_symbol: str
    currency_name: str
    route: Literal["faq", "transfer", "compliance", "rewards", "support"]
    response: str
    agent_used: str
    agent_emoji: str


# ─────────────────────────────────────────────────────────────────
# Knowledge Bases  (sourced directly from the Ajeer website)
# ─────────────────────────────────────────────────────────────────

FAQ_KB = """
## What is Ajeer?
Ajeer (trading name of Monex International Limited) is a digital money transfer and 
remittance platform. It lets you send money internationally to bank accounts, mobile 
wallets, or cash collectors — fast, securely, and with real exchange rates. 
Monex International Ltd is authorised by the FCA as a Small Payment Institution (FRN: 510848).
Registered address: 32 Spring Street, Paddington, London, W2 1JA.

## Who can use Ajeer?
Anyone who meets the eligibility criteria — including age (18+), residency, and identity 
verification requirements — can use the app to send money.

## What currencies does Ajeer support?
Ajeer lets you hold 6+ currencies and send to 30+ currencies including USD, AED, SAR, 
INR, GBP, EUR, PKR, and more. Exchange rates are real market rates with no hidden markups.

## Is Ajeer available on mobile?
Yes. The Ajeer app is available on the App Store and Google Play Store.

## What payout methods are available?
Recipients can receive funds via: bank account transfer, mobile wallet, or cash collector.

## What are the key features?
- Same-day transfers on most major currencies
- Real exchange rates (bank-beating rates)
- Hold 6+ currencies in one account
- eSIM product for travel (instant data in 100+ countries, no physical SIM needed)
- Prepaid Ajeer card (globally accepted, spend anywhere, no minimum balance)
- Freelancer/Non-Resident remittance support
- Repeat transfers with saved beneficiaries

## How do I create an account?
Click 'Register' or 'Sign up' on the Ajeer website or app. You'll need basic 
identification documents for electronic identity verification.

## What are the contact details?
Email: cs@Ajeer.money
Post: Compliance Department, Monex International Ltd, 32 Spring Street, Paddington, W2 1JA, UK
"""

TRANSFER_KB = """
## How do I send money?
Step 1: Select the destination country
Step 2: Enter the beneficiary details or create a new beneficiary
Step 3: Choose the payout method (bank account / mobile wallet / cash collector)
Step 4: Review fees and exchange rate (shown upfront before confirming)
Step 5: Confirm the transfer

## How much does it cost?
Fees are shown upfront before you confirm. Exact cost depends on destination, amount, 
and payout method. Ajeer does not impose hidden fees — exchange rates are real market rates.
Note: Some correspondent banks involved in processing may charge their own fees.

## How long does a transfer take?
Same-day transfers are available on most major currencies. If the Beneficiary Account is 
in the EEA in GBP, EUR or another EEA currency, funds arrive by the end of the next 
Business Day. For EEA accounts in non-EEA currencies, within 4 Business Days.

## Can I save beneficiaries?
Yes. Save beneficiaries to repeat transfers quickly without re-entering details.

## What is a Forward Contract?
A Forward Contract lets you lock in an exchange rate for a future date. Margin (security 
deposit) may be required within 24 hours of the transaction receipt. You can also request 
a pre-delivery or roll-over of the delivery date.

## What is a Limit Order?
A Limit Order executes automatically when your target exchange rate is achieved within 
your specified time window. You can cancel a Limit Order at any time by phone or email 
before the rate is reached.

## Can I cancel a transfer?
A transaction can only be cancelled if it has NOT yet been processed. An admin fee of £3 
applies to cancellations. Once processed, transactions cannot be recalled and refunds 
cannot be given.

## What about wire transfers?
For wire transfers, include your client number as the payment reference. Transfer from 
your registered bank account only. Cash deposits are NOT accepted — if cash is deposited, 
the transaction will not be processed and no refund will be issued.

## What is the Ajeer Card?
The Ajeer prepaid card is globally accepted (Visa/Mastercard), tracks expenses, has no 
minimum balance, and works online and in stores. It enables you to spend in your held 
currencies without conversion fees.

## What is the eSIM product?
Ajeer offers instant data eSIMs for travel in 100+ countries. Activate in seconds, no 
physical SIM needed, and keep your existing number.
"""

COMPLIANCE_KB = """
## Why do I need to verify my identity?
Identity verification is required to comply with:
- Anti-Money Laundering (AML) regulations
- Counter-Terrorist Financing (CTF) regulations
- FCA regulatory requirements (FRN: 510848)
- UK Money Laundering Regulations 2017

You'll need to provide basic identification documents for electronic verification.

## What is KYC?
KYC (Know Your Customer) is the process of verifying your identity. Ajeer may request 
additional documentation to comply with regulatory obligations at any time.

## What laws govern Ajeer?
- Electronic Money Regulations 2011 (EMRs)
- Payment Services Regulations 2017 (PSRs)
- UK Money Laundering Regulations 2017
- Proceeds of Crime Act 2002
- UK Terrorism Act 2000
- UK and international financial sanctions regimes

## Are my funds safe?
Yes. Ajeer is authorised by the FCA. Customer funds are "safeguarded" in segregated bank 
accounts separately from company funds, in accordance with EMRs. In the event of insolvency, 
these funds form a separate asset pool — you are reimbursed in priority to other creditors.
Ajeer uses industry-standard encryption and secure infrastructure.

## What is Ajeer's data protection policy?
Ajeer complies with GDPR 2018. Data Protection Officer: Mr G Kiruba.
Personal data is processed lawfully under the "legitimate interests" condition.
Sensitive personal data is NOT collected or processed. 
Automated decision-taking is NOT used.
You have rights of access, correction, and objection over your data.

## Can my account be suspended?
Yes, Ajeer may suspend accounts on grounds of: security concerns, suspected fraud/unauthorised 
use, AML/CTF compliance, breach of agreement, or insolvency. You will be notified with reasons.

## How is Ajeer regulated?
Ajeer is a trading name of Monex International Limited, FCA-authorised Small Payment 
Institution (FRN: 510848). Registered in England and Wales (Company No. 04974470).
The Financial Services Compensation Scheme (FSCS) does NOT cover Ajeer services.
Unresolved complaints can be referred to the Financial Ombudsman Service (FOS): 
www.financialombudsman.org.uk

## What is the refund policy?
- Once a transaction is processed, it CANNOT be recalled — no refund possible.
- Cancellation (before processing) incurs a £3 admin fee.
- Wire transfers: use client number as payment reference; bank account transfers only.
- Cash deposits are NOT accepted; no refund if cash is deposited.
"""

REWARDS_KB = """
## What is the Ajeer Rewards Program?
The Ajeer Remittance Rewards Program rewards customers who send money internationally 
via the Ajeer app. Both senders (Remitters) and receivers (Beneficiaries) are entered 
into monthly lucky draws to win prizes.

## Who is eligible?
- Individuals aged 18+ and corporates who are UK residents or citizens
- Transactions must be made through the Ajeer app
- Minimum remittance of £100 per transaction to qualify

## How are chances to win calculated?
Chances are earned per transaction based on the amount sent (GBP):

| Amount (GBP)  | Chances to Win |
|--------------|----------------|
| £100 – £299  | 1x (1 chance)  |
| £300 – £499  | 2x (2 chances) |
| £500 – £999  | 3x (3 chances) |
| £1000 – £1999| 4x (4 chances) |
| £2000 – £3499| 5x (5 chances) |
| £3500 – £5000| 6x (6 chances) |
| £5000+       | 6x (6 chances) — CAPPED |

Key rules:
- Multiple transactions in the same month earn more chances
- No cap on total chances per month
- Maximum 6 chances per single transaction
- Chances do NOT roll over to next month
- Chances are non-transferable

## How does the monthly draw work?
- Separate draws for Remitters and Beneficiaries each month
- 3 winners selected from Remitters' pool, 3 from Beneficiaries' pool
- Winners selected via computerized random selection
- A participant may only win once per draw per month
- Remitter winners announced on Ajeer social media and app/website
- Beneficiary winners announced on social media and participating bank website

## What prizes can I win?
Prizes include:
- Umrah tickets for two (complete pilgrimage packages for 2 people)
- Premium Electronics (smartphones, laptops, tablets)
- Lifestyle Rewards (fashion accessories, home appliances, exclusive vouchers)
All prizes are gifted by Bogo Technologies (Private) Limited under the Bogo Liv brand.

## Beneficiary bonus reward
Beneficiaries who receive a total of £200 or more through the Ajeer app in a calendar month 
automatically receive 1 month of complimentary Gold membership on the Bogo Liv app.

## How will I be notified if I win?
- Remitter winners: contacted by phone, and possibly email or in-app message
- Beneficiary winners: contacted by phone
- Prizes must be claimed within 15 days of notification — failure may result in disqualification
- Proof of identity and transaction verification may be required to claim prizes

## Can prizes be transferred or exchanged?
No. Prizes are non-transferable and non-exchangeable. Ajeer may substitute prizes without notice.
"""

SUPPORT_KB = """
## How do I contact Ajeer support?
Email: cs@Ajeer.money
Post: Compliance Department, Monex International Ltd, 32 Spring Street, Paddington, W2 1JA, UK
Phone: See https://Ajeer.money/supporthome for support telephone numbers
Contact form: Available at https://Ajeer.money/contact

## How do I make a complaint?
Contact Ajeer in writing:
- Email: cs@Ajeer.money
- Post: Compliance Department, Monex International Ltd, 32 Spring Street, Paddington, W2 1JA

If unresolved, refer to the Financial Ombudsman Service (FOS): www.financialombudsman.org.uk
You may also contact the FCA: 0800 111 6768 (freephone).
EU customers can use the European Commission's Online Dispute Resolution platform: ec.europe.eu/adr

## How do I close my account?
Give at least 1 month's prior written notice to Ajeer. Remaining funds will be transferred 
to your nominated bank account after deducting any amounts owed. All pending trades will be 
closed out.

## Can Ajeer close my account without notice?
Yes, immediately if: fraudulent/illegal use is detected, required by law/regulator, 
or in breach of the agreement. Otherwise, Ajeer gives 2 months' notice.

## What happens to my money if Ajeer becomes insolvent?
Customer funds are held in segregated accounts (safeguarded) per EMR requirements. 
A third-party backup servicer will be appointed to administer pending transfers and 
handle payments. You are reimbursed from the segregated pool in priority to other creditors.
Note: Ajeer is NOT covered by the Financial Services Compensation Scheme (FSCS).

## How do I update my account details?
Contact Ajeer as soon as possible if your name, address, authorised parties, or financial 
position changes materially. Use cs@Ajeer.money or call an Ajeer Representative.

## What if a payment went to the wrong account?
If you provided incorrect details, Ajeer is not liable but will use reasonable efforts to 
recover the payment. Reasonable costs may be charged for recovery attempts.

## What if there was an unauthorised payment?
Notify Ajeer without undue delay (within 13 months) via cs@Ajeer.money. Ajeer will 
immediately refund unauthorised payments subject to investigation. If fraud or gross 
negligence on your part is proven, you may bear liability.

## What is the Data Protection Officer contact?
DPO: Mr G Kiruba. Contact through cs@Ajeer.money for GDPR-related queries.
"""


# ─────────────────────────────────────────────────────────────────
# Node 1: Supervisor — classifies and routes
# ─────────────────────────────────────────────────────────────────
def supervisor_node(state: AgentState) -> AgentState:
    msg = state["user_message"].lower()

    # Fast keyword routing
    transfer_kw = [
        "send money",
        "transfer",
        "how to send",
        "fee",
        "fees",
        "cost",
        "beneficiary",
        "payout",
        "exchange rate",
        "forward contract",
        "limit order",
        "cancel",
        "wire",
        "esim",
        "card",
        "how long",
        "how much",
        "receive",
        "destination",
        "iban",
        "swift",
    ]
    compliance_kw = [
        "verify",
        "kyc",
        "aml",
        "identity",
        "document",
        "regulated",
        "fca",
        "law",
        "legal",
        "gdpr",
        "data",
        "privacy",
        "safe",
        "suspend",
        "fraud",
        "secure",
        "regulation",
        "compliance",
        "insolvency",
        "safeguard",
    ]
    rewards_kw = [
        "reward",
        "rewards",
        "prize",
        "draw",
        "lucky",
        "chances",
        "win",
        "umrah",
        "bogo",
        "electronics",
        "voucher",
        "points",
        "eligible",
        "beneficiary win",
        "how to earn",
        "monthly draw",
    ]
    support_kw = [
        "complaint",
        "problem",
        "issue",
        "close account",
        "contact",
        "wrong account",
        "unauthorised",
        "unauthorized",
        "refund",
        "support",
        "help",
        "error",
        "dispute",
        "ombudsman",
        "update details",
        "dpo",
        "compensation",
    ]

    def match(keywords):
        return any(kw in msg for kw in keywords)

    if match(transfer_kw):
        route = "transfer"
    elif match(compliance_kw):
        route = "compliance"
    elif match(rewards_kw):
        route = "rewards"
    elif match(support_kw):
        route = "support"
    else:
        # Ask Gemini to classify ambiguous messages
        prompt = """Classify this message from an Ajeer remittance platform user into one category.
Respond with ONLY the single category word.

Categories:
- faq         → general questions about Ajeer, what it is, who can use it, features
- transfer    → sending money, transfer steps, fees, exchange rates, beneficiaries, FX contracts, card, eSIM
- compliance  → KYC, identity verification, AML, data privacy, GDPR, regulations, account security
- rewards     → rewards program, lucky draw, chances to win, prizes, Bogo Liv, Umrah
- support     → complaints, account issues, wrong transfers, unauthorised payments, contact, refunds

Message: "{msg}"
Category:""".format(
            msg=state["user_message"]
        )
        try:
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            result = model.generate_content(prompt)
            route_raw = result.text.strip().lower().split()[0]
            route = (
                route_raw
                if route_raw in ["faq", "transfer", "compliance", "rewards", "support"]
                else "faq"
            )
        except Exception:
            route = "faq"

    return {
        **state,
        "route": route,
        "response": "",
        "agent_used": "",
        "agent_emoji": "",
    }


# ─────────────────────────────────────────────────────────────────
# Node 2: FAQ Agent
# ─────────────────────────────────────────────────────────────────
def faq_agent_node(state: AgentState) -> AgentState:
    system = f"""You are the Ajeer FAQ Agent. Ajeer is a UK-based digital money transfer 
and remittance platform, operated by Monex International Limited (FCA FRN: 510848).

Answer the user's question using the knowledge base below. Be friendly, concise, and accurate.
If the answer isn't in the knowledge base, say so and direct them to cs@Ajeer.money.
Do not make up information. Format with short paragraphs — no excessive bullet points.

KNOWLEDGE BASE:
{FAQ_KB}"""
    response = _gemini(system, state["user_message"], state["history"])
    return {
        **state,
        "response": response,
        "agent_used": "FAQ Agent",
        "agent_emoji": "📋",
    }


# ─────────────────────────────────────────────────────────────────
# Node 3: Transfer Agent
# ─────────────────────────────────────────────────────────────────
def transfer_agent_node(state: AgentState) -> AgentState:
    system = f"""You are the Ajeer Transfer Agent. Ajeer is a digital remittance platform.
You help users understand how to send money, what fees apply, exchange rates, payout methods,
transfer timelines, Forward Contracts, Limit Orders, the Ajeer Card, eSIM, and more.

The user is: {state['user_name']} from {state['user_country']} 
(their currency: {state['currency_symbol']} {state['currency_code']} — {state['currency_name']})

Answer clearly and practically. If the question involves specific fees or live rates, note that 
fees are shown upfront in the app before confirmation. Direct to the app or cs@Ajeer.money 
for live quotes. Do not invent specific exchange rates.

KNOWLEDGE BASE:
{TRANSFER_KB}"""
    response = _gemini(system, state["user_message"], state["history"])
    return {
        **state,
        "response": response,
        "agent_used": "Transfer Agent",
        "agent_emoji": "💸",
    }


# ─────────────────────────────────────────────────────────────────
# Node 4: Compliance Agent
# ─────────────────────────────────────────────────────────────────
def compliance_agent_node(state: AgentState) -> AgentState:
    system = f"""You are the Ajeer Compliance Agent. You answer questions about identity 
verification, KYC/AML requirements, data privacy (GDPR), FCA regulation, account security, 
safeguarding of funds, and legal/regulatory matters.

Be accurate and reassuring. Use clear plain English — avoid excessive legal jargon. 
For complex legal matters, direct users to cs@Ajeer.money or the appropriate authority.
NEVER give specific legal advice — only explain Ajeer's policies and regulations as documented.

KNOWLEDGE BASE:
{COMPLIANCE_KB}"""
    response = _gemini(system, state["user_message"], state["history"])
    return {
        **state,
        "response": response,
        "agent_used": "Compliance Agent",
        "agent_emoji": "🛡️",
    }


# ─────────────────────────────────────────────────────────────────
# Node 5: Rewards Agent
# ─────────────────────────────────────────────────────────────────
def rewards_agent_node(state: AgentState) -> AgentState:
    system = f"""You are the Ajeer Rewards Agent. You explain the Ajeer Remittance Rewards 
Program in detail — how to earn chances, the monthly lucky draw process, prizes (Umrah tickets, 
electronics, lifestyle rewards), Bogo Liv Gold membership, and eligibility rules.

Be enthusiastic but accurate. Help users understand how to maximise their chances.
Do not promise specific prizes — note that Ajeer may substitute prizes without prior notice.

KNOWLEDGE BASE:
{REWARDS_KB}"""
    response = _gemini(system, state["user_message"], state["history"])
    return {
        **state,
        "response": response,
        "agent_used": "Rewards Agent",
        "agent_emoji": "🎁",
    }


# ─────────────────────────────────────────────────────────────────
# Node 6: Support Agent
# ─────────────────────────────────────────────────────────────────
def support_agent_node(state: AgentState) -> AgentState:
    system = f"""You are the Ajeer Support Agent. You help users with complaints, account 
issues, unauthorised payments, wrong transfers, account closure, updating details, and 
contacting Ajeer or regulators.

Always be empathetic and solution-focused. Provide the correct contact information:
- Email: cs@Ajeer.money
- Phone: https://Ajeer.money/supporthome
- Post: Compliance Dept, Monex International Ltd, 32 Spring Street, Paddington, W2 1JA
- FOS (complaints): www.financialombudsman.org.uk
- FCA: 0800 111 6768

If someone reports fraud or an unauthorised payment, treat it urgently and tell them to 
contact Ajeer immediately at cs@Ajeer.money.

KNOWLEDGE BASE:
{SUPPORT_KB}"""
    response = _gemini(system, state["user_message"], state["history"])
    return {
        **state,
        "response": response,
        "agent_used": "Support Agent",
        "agent_emoji": "🎧",
    }


# ─────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────
def route_decision(state: AgentState) -> str:
    return state.get("route", "faq")


# ─────────────────────────────────────────────────────────────────
# Graph Builder
# ─────────────────────────────────────────────────────────────────
def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("faq", faq_agent_node)
    graph.add_node("transfer", transfer_agent_node)
    graph.add_node("compliance", compliance_agent_node)
    graph.add_node("rewards", rewards_agent_node)
    graph.add_node("support", support_agent_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_decision,
        {
            "faq": "faq",
            "transfer": "transfer",
            "compliance": "compliance",
            "rewards": "rewards",
            "support": "support",
        },
    )

    for node in ["faq", "transfer", "compliance", "rewards", "support"]:
        graph.add_edge(node, END)

    return graph.compile()


# ─────────────────────────────────────────────────────────────────
# Public API — called from Flask
# ─────────────────────────────────────────────────────────────────
def run_agent(
    message: str,
    history: list[dict],
    user_name: str,
    user_country: str,
    currency_code: str,
    currency_symbol: str,
    currency_name: str,
    db=None,  # kept for API compatibility, not used in this version
) -> dict:
    graph = build_agent_graph()

    initial_state: AgentState = {
        "user_message": message,
        "history": history,
        "user_name": user_name,
        "user_country": user_country,
        "currency_code": currency_code,
        "currency_symbol": currency_symbol,
        "currency_name": currency_name,
        "route": "faq",
        "response": "",
        "agent_used": "",
        "agent_emoji": "",
    }

    result = graph.invoke(initial_state)

    return {
        "reply": result.get("response", "I encountered an error. Please try again."),
        "agent_used": result.get("agent_used", "FAQ Agent"),
        "agent_emoji": result.get("agent_emoji", "📋"),
        "route": result.get("route", "faq"),
        "sources": ["Ajeer Knowledge Base"],
    }

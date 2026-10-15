# MatchWise - AI Resume Analyser

A Streamlit tool that scores a resume against a job description using Google Gemini, then
reports what is missing.

## What it does

- **Match score** between the resume and the job description
- **Missing keywords** - skills the JD asks for that the resume never mentions
- **Profile summary** written from the resume
- **Improvement suggestions**, returned as structured JSON so the UI can render them reliably

## Why structured output matters

Asking a language model for free-form advice gives you something different every run. This asks
Gemini for JSON with a fixed shape and parses it, with error handling for the cases where the
model wraps its reply in markdown fences. That is the difference between a demo and something
you can put a UI on top of.

## Stack

| | |
|---|---|
| UI | Streamlit |
| Model | Google Gemini via `google-genai` |
| Config | `python-dotenv` |

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env     # then paste your own key into .env
streamlit run ats_gemini.py
```

Get a free API key at https://aistudio.google.com/apikey

## A note on secrets

This repository ships `.env.example` only. Real keys stay in `.env`, which `.gitignore`
excludes. If you fork it, never commit your own `.env`.

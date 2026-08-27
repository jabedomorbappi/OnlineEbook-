# Digital Library

A web app that turns PDFs stored in Google Drive into a real book-like
reading experience.

## Stack
- **Backend:** Django + Django REST Framework, PostgreSQL
- **Frontend:** Next.js + Tailwind CSS
- **PDF processing:** PyMuPDF (text extraction, reflowed into book pages)
- **Source of content:** Google Drive (accessed via a service account)

## How it works
1. PDFs live in organized folders in Google Drive.
2. Django syncs with Drive (service account), downloads PDFs, and extracts
   text per page using PyMuPDF.
3. Certain sections/pages can be marked to skip (e.g. covers, references)
   via "skip rules" stored in the database.
4. Django exposes a REST API that serves book metadata and one page of
   content at a time (skip-aware).
5. Next.js renders this as an actual page-turning book UI — not a PDF
   viewer or plain text dump.

## Project structure


## Status
🚧 In development — currently building backend foundation.

## Setup
Setup instructions will be added as each part of the project is built.
